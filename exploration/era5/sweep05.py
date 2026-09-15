"""Sweep ERA5 single-level variables with candidates derived from each variable's requirements.

Every candidate is scored with the official `check_safety_requirements`, so a
candidate is only kept if it truly passes. Mean-error bounds are exploited
directly (unwrapped quantisers), because the default safeguards would turn
them into much stricter pointwise bounds.

    python sweep05.py [workers] [var ...]
"""

import contextlib
import io
import json
import lzma
import sys
import time
import traceback
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
TIME = "2026-07-15T12:00:00"
E = 9 | lzma.PRESET_EXTREME
import os
OUT = HERE / os.environ.get("SWEEP05_OUT", "results05")


def load(v):
    p = HERE / "cache" / f"single_{v}.npy"
    if not p.exists():
        import era5_loader as L

        ds = L.load_era5_data(leveltype="single", param=v)
        np.save(p, ds[L._var_name(ds, v)].sel(time=TIME).values)
    return np.load(p)


def leaves(req):
    kind = req.kind.name
    if kind in ("any", "all"):
        for r in req.requirements:
            yield from leaves(r)
    else:
        yield req


def candidates(x, reqs):
    from compression_requirement_safeguards import safeguards_for_requirements
    from numcodecs import LZMA, FixedScaleOffset
    from numcodecs.packbits import PackBits
    from numcodecs_combinators.framed import FramedCodecStack
    from numcodecs_combinators.stack import CodecStack
    from numcodecs_mask import MaskMetaCodec
    from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
    from numcodecs_replace import ReplaceFilterCodec
    from numcodecs_safeguards import SafeguardedCodec
    from numcodecs_wasm_zstd import Zstd
    from numcodecs_zero import ZeroCodec

    finite = np.isfinite(x)
    has_nan = not finite.all()
    xf = x[finite]
    dtype = x.dtype.str
    if xf.size == 0:
        return {}
    amax = float(np.max(np.abs(xf)))
    mean_abs = float(np.mean(np.abs(xf)))

    def lz(size):
        return LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": size}, {"id": lzma.FILTER_LZMA2, "preset": E, "lc": 1, "lp": 1, "pb": 1}])

    def int_type(span):
        return ("<i1", 1) if span < 120 else ("<i2", 2) if span < 32000 else ("<i4", 4) if span < 2e9 else (None, None)

    def masked(stack):  # stack: list of codecs that expect finite input
        if not has_nan:
            return FramedCodecStack(*stack)
        return MaskMetaCodec(
            mask=np.nan,
            codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: "finite_mean"}), *stack),
            bitmap_codec=CodecStack(PackBits(), LZMA(preset=E)),
        )

    def absq(eb):  # pointwise |err| <= eb on a zero-anchored 2*eb grid
        if not (eb > 0):
            return None
        step = 2 * eb * 0.9999
        dt, size = int_type(amax / step + 2)
        if dt is None:
            return None
        return masked([FixedScaleOffset(offset=0, scale=1 / step, dtype=dtype, astype=dt), lz(size)])

    def relq(ratio):  # pointwise ratio bound via log2 grid
        step = 2 * np.log2(ratio) * 0.9999
        inner = FixedScaleOffset(offset=0, scale=1 / step, dtype="<f8", astype="<i2").get_config()
        pw = PointwiseRatioErrorBoundedCodec(eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec=inner, sign_codec=Zstd(level=19))
        return CodecStack(pw, lz(2)) if not has_nan else MaskMetaCodec(
            mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: "finite_mean"}), pw, lz(2)),
            bitmap_codec=CodecStack(PackBits(), LZMA(preset=E)))

    full_sg = safeguards_for_requirements(*reqs)
    limit_reqs = [r for r in reqs if r.kind.name == "data_limits"]
    limit_sg = safeguards_for_requirements(*limit_reqs) if limit_reqs else None

    # name -> (builder, ladder group); within a ladder, candidates are ordered
    # loosest first and the rest of the ladder is skipped after the first pass
    c = {"Safeguarded(Zero)": (lambda: SafeguardedCodec(codec=ZeroCodec(), safeguards=full_sg), None)}

    def add(name, make, wrap_full=False, group=None):
        c[name] = (make, group)
        if limit_sg is not None:
            c[f"LimitsSafeguarded({name})"] = (lambda: SafeguardedCodec(codec=make(), safeguards=limit_sg), group and f"{group}+limits")
        if wrap_full:
            c[f"Safeguarded({name})"] = (lambda: SafeguardedCodec(codec=make(), safeguards=full_sg), None)

    LADDER = tuple(float(k) for k in os.environ.get("SWEEP05_LADDER", "16,11,8,5.6,4,2.8,2,1.4,1.0").split(","))
    for leaf in {(r.kind.name, float(getattr(r, "value", 0) or 0)) for req in reqs for r in leaves(req)}:
        kind, v = leaf
        if kind == "max_pointwise_absolute_error_bound" and v > 0:
            add(f"absq pointwise {v:g}", lambda v=v: absq(v), wrap_full=True)
        elif kind == "max_pointwise_relative_error_bound" and v > 0:
            add(f"relq pointwise {v:g}", lambda v=v: relq(1 + v), wrap_full=True)
        elif kind == "mean_absolute_error_bound" and v > 0:
            for k in LADDER:
                add(f"absq meanabs {v:g} eb={k}v", lambda v=v, k=k: absq(k * v), group=f"meanabs{v:g}")
        elif kind == "mean_relative_error_bound" and v > 0:
            for k in LADDER:
                add(f"absq meanrel {v:g} eb={k}v*mean|x|", lambda v=v, k=k: absq(k * v * mean_abs), group=f"meanrel-abs{v:g}")
            for k in (4, 2.8, 1.9, 1.4):
                add(f"relq meanrel {v:g} ratio=1+{k}v", lambda v=v, k=k: relq(1 + k * v), group=f"meanrel-rel{v:g}")
        elif kind == "lossless":
            add("lossless LZMA", lambda: FramedCodecStack(LZMA(preset=E)))
            ints = np.all(xf == np.round(xf)) and xf.min() >= -128 and xf.max() <= 127
            if ints:
                add("lossless int8 grid + LZMA", lambda: masked([FixedScaleOffset(offset=0, scale=1, dtype=dtype, astype="<i1"), LZMA(preset=E)]))
    return c


def run_var(v):
    from compression_recommendations import Recommendations
    from compression_requirement_checks import check_safety_requirements

    out_path = OUT / f"{v}.json"
    if out_path.exists():
        return json.loads(out_path.read_text())
    rows = []
    try:
        x = load(v)
        reqs = list(Recommendations.provide.search(markers={"grib-short-name": v, "level-kind": "single"}))
        passed_groups = set()
        for name, (make, group) in candidates(x, reqs).items():
            if group is not None and group in passed_groups:
                continue
            try:
                codec = make()
                if codec is None:
                    continue
                t = time.time()
                enc = codec.encode(x)
                dec = np.asarray(codec.decode(enc)).reshape(x.shape)
                te = time.time() - t
                with contextlib.redirect_stdout(io.StringIO()):
                    ok = bool(check_safety_requirements(original=x, reconstructed=dec, requirements=reqs))
                rows.append(dict(var=v, codec=name, cr=round(x.nbytes / np.array(enc).nbytes, 3), ok=ok, sec=round(te, 2), config=codec.get_config()))
                if ok and group is not None:
                    passed_groups.add(group)
            except Exception as e:  # noqa: BLE001
                rows.append(dict(var=v, codec=name, error=f"{type(e).__name__}: {str(e)[:160]}"))
        rows.insert(0, dict(var=v, requirements=[r.humanise() for r in reqs], nan_fraction=float(np.mean(~np.isfinite(x)))))
    except Exception:  # noqa: BLE001
        rows = [dict(var=v, fatal=traceback.format_exc()[-500:])]
    out_path.write_text(json.dumps(rows, indent=1, default=str))
    best = max((r for r in rows if r.get("ok")), key=lambda r: r["cr"], default=None)
    print(f"{v}: " + (f"best {best['cr']} {best['codec']}" if best else "NO PASSING CODEC " + str([r.get("error") or r.get("fatal") for r in rows][:2])), flush=True)
    return rows


if __name__ == "__main__":
    import era5_loader as L
    from compression_recommendations import Recommendations

    OUT.mkdir(exist_ok=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    if len(sys.argv) > 2:
        vars_ = sys.argv[2:]
    else:
        cat = L.load_era5_catalog(leveltype="single")
        vars_ = []
        for v in sorted({v for g in cat["groups"].values() for v in g["variables"]}):
            try:
                Recommendations.provide.search(markers={"grib-short-name": v, "level-kind": "single"})
                vars_.append(v)
            except KeyError:
                pass
    print(f"sweeping {len(vars_)} variables with {workers} workers", flush=True)
    with Pool(workers, maxtasksperchild=4) as pool:
        for _ in pool.imap_unordered(run_var, vars_):
            pass
    print("DONE05")
