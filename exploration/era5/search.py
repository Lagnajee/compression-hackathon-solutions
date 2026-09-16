"""Search each codec family for its loosest setting that still passes the checks.

For every ERA5 variable, codec families are derived from the variable's
requirement tree. Each family has one scalar looseness parameter `p` (a
multiple of the requirement's bound). The search doubles `p` until the official
`check_safety_requirements` fails, then bisects between the last pass and the
first failure. Every evaluated setting is logged, so the export step can pick
the best passing codec per variable across all sweeps.

    uv run python exploration/era5/search.py <pressure|single> <workers> [var ...]
"""

import contextlib
import io
import json
import lzma
import math
import sys
import time
import traceback
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
E = 9 | lzma.PRESET_EXTREME
BISECT_STEPS = 3


def leaves(req):
    if req.kind.name in ("any", "all"):
        for r in req.requirements:
            yield from leaves(r)
    else:
        yield req


def families(x, reqs):
    """Return a list of (name, builder(p) -> codec | None, p_start, p_max)."""
    from compression_requirement_safeguards import safeguards_for_requirements
    from numcodecs import LZMA, FixedScaleOffset
    from numcodecs.packbits import PackBits
    from numcodecs_combinators.framed import FramedCodecStack
    from numcodecs_combinators.stack import CodecStack
    from numcodecs_mask import MaskMetaCodec
    from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
    from numcodecs_replace import ReplaceFilterCodec
    from numcodecs_safeguards import SafeguardedCodec
    from numcodecs_tokenize import TokenizeCodec
    from numcodecs_wasm_sperr import Sperr
    from numcodecs_wasm_sz3 import Sz3
    from numcodecs_wasm_zstd import Zstd

    finite = np.isfinite(x)
    has_nan = not bool(finite.all())
    xf = x[finite]
    if xf.size == 0:
        return []
    amax = float(np.max(np.abs(xf)))
    mean_abs = float(np.mean(np.abs(xf)))
    dtype = x.dtype.str

    full_sg = safeguards_for_requirements(*reqs)
    limit_reqs = [r for r in reqs if r.kind.name == "data_limits"]
    limit_sg = safeguards_for_requirements(*limit_reqs) if limit_reqs else None

    def lzma_outer(c):
        return CodecStack(c, LZMA(preset=E))

    def nan_safe(c):
        if not has_nan:
            return c
        return MaskMetaCodec(
            mask=np.nan,
            codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: "finite_mean"}), c),
            bitmap_codec=CodecStack(PackBits(), LZMA(preset=E)),
        )

    def limits(c):
        return SafeguardedCodec(codec=c, safeguards=limit_sg) if limit_sg is not None else c

    def full(c):
        return SafeguardedCodec(codec=c, safeguards=full_sg)

    def grid(eb):
        step = 2 * eb * 0.9999
        span = amax / step + 2
        dt, size = ("<i1", 1) if span < 120 else ("<i2", 2) if span < 32000 else ("<i4", 4) if span < 2e9 else (None, None)
        if dt is None:
            return None
        stack = [FixedScaleOffset(offset=0, scale=1 / step, dtype=dtype, astype=dt),
                 LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": size}, {"id": lzma.FILTER_LZMA2, "preset": E, "lc": 1, "lp": 1, "pb": 1}])]
        return FramedCodecStack(*stack) if not has_nan else nan_safe(CodecStack(*stack))

    def pw(inner_cfg, key, ratio):
        return PointwiseRatioErrorBoundedCodec(
            eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec={**inner_cfg, key: "$eb_abs"}, sign_codec=Zstd(level=19)
        )

    sz3_cfg = Sz3(eb_mode="abs", eb_abs=1.0).get_config()
    sperr_cfg = Sperr(mode="pwe", pwe=1.0).get_config()
    fams = []

    def abs_families(tag, base, wrap, p_max):
        if not base > 0:
            return
        fams.append((f"{tag} grid", lambda p: (lambda g: None if g is None else wrap(g))(grid(p * base)), 1.0, p_max))
        fams.append((f"{tag} SZ3 abs", lambda p: lzma_outer(wrap(nan_safe(Sz3(eb_mode="abs", eb_abs=p * base)))), 1.0, p_max))
        fams.append((f"{tag} SPERR pwe", lambda p: lzma_outer(wrap(nan_safe(Sperr(mode="pwe", pwe=p * base)))), 1.0, p_max))
        fams.append((f"{tag} SPERR q", lambda p: lzma_outer(wrap(nan_safe(Sperr(mode="q", q=p * base)))), 1.0, p_max))

    def rel_families(tag, v, wrap, p_max):
        if not v > 0:
            return
        fams.append((f"{tag} PwRatio(SZ3)", lambda p: lzma_outer(wrap(nan_safe(pw(sz3_cfg, "eb_abs", (1 + v) ** p)))), 1.0, p_max))
        fams.append((f"{tag} PwRatio(SPERR)", lambda p: lzma_outer(wrap(nan_safe(pw(sperr_cfg, "pwe", (1 + v) ** p)))), 1.0, p_max))

    seen = set()
    for req in reqs:
        for leaf in leaves(req):
            kind, v = leaf.kind.name, float(getattr(leaf, "value", 0) or 0)
            if (kind, v) in seen:
                continue
            seen.add((kind, v))
            if kind == "mean_absolute_error_bound":
                abs_families(f"meanabs {v:g}", v, limits, 1024.0)
            elif kind == "mean_relative_error_bound":
                abs_families(f"meanrel {v:g} (abs)", v * mean_abs, limits, 1024.0)
                rel_families(f"meanrel {v:g}", v, limits, 64.0)
            elif kind == "max_pointwise_absolute_error_bound":
                abs_families(f"pwabs {v:g} safeguarded", v, full, 16.0)
            elif kind == "max_pointwise_relative_error_bound":
                rel_families(f"pwrel {v:g} safeguarded", v, full, 16.0)
            elif kind == "lossless":
                fams.append(("lossless Tokenize+LZMA", lambda p: FramedCodecStack(TokenizeCodec(), LZMA(preset=E)), 1.0, 1.0))
    return fams


def evaluate(x, reqs, codec):
    from compression_requirement_checks import check_safety_requirements

    enc = codec.encode(x)
    dec = np.asarray(codec.decode(enc)).reshape(x.shape)
    with contextlib.redirect_stdout(io.StringIO()):
        ok = bool(check_safety_requirements(original=x, reconstructed=dec, requirements=reqs))
    return ok, x.nbytes / np.array(enc).nbytes


def run_var(args):
    level, var = args
    from hackathon import era5

    out = ROOT / "exploration" / "era5" / f"search_{level}" / f"{var}.json"
    if out.exists():
        return var, json.loads(out.read_text())
    rows = []
    try:
        x = era5.field(level, var)
        reqs = era5.requirements(level, var)
        rows.append(dict(var=var, requirements=[r.humanise() for r in reqs]))

        def trial(name, build, p):
            codec = build(p)
            if codec is None:
                return False
            t = time.time()
            try:
                ok, cr = evaluate(x, reqs, codec)
                rows.append(dict(var=var, codec=f"{name} p={p:.4g}", cr=round(cr, 3), ok=ok, sec=round(time.time() - t, 1), config=codec.get_config()))
                return ok
            except Exception as e:  # noqa: BLE001
                rows.append(dict(var=var, codec=f"{name} p={p:.4g}", error=f"{type(e).__name__}: {str(e)[:160]}"))
                return False

        for name, build, p, p_max in families(x, reqs):
            last_ok, first_fail = None, None
            while p <= p_max:
                if trial(name, build, p):
                    last_ok, p = p, p * 2
                else:
                    first_fail = p
                    break
            if last_ok is not None and first_fail is not None:
                for _ in range(BISECT_STEPS):
                    mid = math.sqrt(last_ok * first_fail)
                    if trial(name, build, mid):
                        last_ok = mid
                    else:
                        first_fail = mid
    except Exception:  # noqa: BLE001
        rows.append(dict(var=var, fatal=traceback.format_exc()[-600:]))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=1, default=str))
    return var, rows


def main():
    level, workers = sys.argv[1], int(sys.argv[2])
    variables = sys.argv[3:]
    if not variables:
        expected = json.loads((ROOT / "results" / "era5_expected.json").read_text())
        variables = sorted(k.split("/", 1)[1] for k in expected if k.startswith(f"{level}/"))
    print(f"searching {len(variables)} {level}-level variables with {workers} workers", flush=True)
    with Pool(workers, maxtasksperchild=2) as pool:
        for var, rows in pool.imap_unordered(run_var, [(level, v) for v in variables]):
            passing = [r for r in rows if r.get("ok")]
            best = max(passing, key=lambda r: r["cr"], default=None)
            fatal = next((r["fatal"] for r in rows if "fatal" in r), None)
            print(f"{var}: " + (f"best {best['cr']} {best['codec']}" if best else f"no pass {fatal or ''}"[:200]), flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
