"""Round 2 for ERA5 pressure-level variables: safeguarded SPERR and LZMA-stacked variants."""
import contextlib, io, json, lzma, time, traceback
import numpy as np
from multiprocessing import Pool
from pathlib import Path
from sweep04 import load

HERE = Path(__file__).parent
E = 9 | lzma.PRESET_EXTREME
ABS = {"u": 0.5, "v": 0.5, "z": 10.0, "w": 0.01, "pv": 1e-7, "t": 0.05}
REL = {"cc": 1.01, "ciwc": 1.01, "clwc": 1.01, "crwc": 1.01, "cswc": 1.01, "o3": 1.01, "q": 1.01, "r": 1.01, "t": 1.01, "d": 1.05, "vo": 1.05, "w": 1.05, "pv": 1.1}
VARS = sorted(set(ABS) | set(REL))


def candidates(v, reqs):
    from compression_requirement_safeguards import safeguards_for_requirements
    from numcodecs import LZMA, FixedScaleOffset
    from numcodecs_combinators.stack import CodecStack
    from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
    from numcodecs_safeguards import SafeguardedCodec
    from numcodecs_wasm_sperr import Sperr
    from numcodecs_wasm_zstd import Zstd
    from numcodecs_zero import ZeroCodec

    sg = safeguards_for_requirements(*reqs)
    S = lambda inner: SafeguardedCodec(codec=inner, safeguards=sg)
    L = lambda c: CodecStack(c, LZMA(preset=E))
    c = {"Safeguarded(Zero)+LZMA": lambda: L(S(ZeroCodec()))}
    if v in ABS:
        eb = ABS[v]
        c[f"Sperr pwe {eb}+LZMA"] = lambda: L(Sperr(mode="pwe", pwe=eb))
        for m in (1.0, 1.5, 2.0):
            c[f"Safeguarded(Sperr pwe {m}*{eb})+LZMA"] = lambda m=m: L(S(Sperr(mode="pwe", pwe=m * eb)))
        for m in (1.5, 2.0, 3.0):
            c[f"Safeguarded(Sperr q {m}*{eb})+LZMA"] = lambda m=m: L(S(Sperr(mode="q", q=m * eb)))
    if v in REL:
        r = REL[v]
        pw_sperr = lambda: PointwiseRatioErrorBoundedCodec(eb_ratio=r, eb_abs_marker="$eb_abs", log_codec={**Sperr(mode="pwe", pwe=1.0).get_config(), "pwe": "$eb_abs"}, sign_codec=Zstd(level=19))
        c[f"PWRatio(Sperr pwe r={r})+LZMA"] = lambda: L(pw_sperr())
        c[f"Safeguarded(PWRatio(Sperr pwe r={r}))+LZMA"] = lambda: L(S(pw_sperr()))
        step = 2 * np.log2(r) * 0.9999
        for dist, lc, lp, pb in ((2, 0, 1, 1), (2, 3, 1, 1), (4, 1, 1, 1)):
            inner = FixedScaleOffset(offset=0, scale=1 / step, dtype="<f8", astype="<i2").get_config()
            c[f"PWRatio(FSO log2 i2 r={r})+LZMA d{dist} lc{lc}"] = lambda inner=inner, dist=dist, lc=lc, lp=lp, pb=pb: CodecStack(
                PointwiseRatioErrorBoundedCodec(eb_ratio=r, eb_abs_marker="$eb_abs", log_codec=inner, sign_codec=Zstd(level=19)),
                LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": dist}, {"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": lp, "pb": pb}]))
    return c


def run_var(v):
    from compression_recommendations import Recommendations
    from compression_requirement_checks import check_safety_requirements
    rows = []
    try:
        x = load(v)
        reqs = Recommendations.provide.search(markers={"grib-short-name": v, "level-kind": "pressure"})
        for name, make in candidates(v, reqs).items():
            try:
                codec = make()
                t = time.time(); enc = codec.encode(x); dec = np.asarray(codec.decode(enc)).reshape(x.shape); te = time.time() - t
                with contextlib.redirect_stdout(io.StringIO()):
                    ok = bool(check_safety_requirements(original=x, reconstructed=dec, requirements=reqs))
                row = dict(var=v, codec=name, cr=round(x.nbytes / np.array(enc).nbytes, 3), ok=ok, sec=round(te, 1), config=codec.get_config())
            except Exception as e:  # noqa: BLE001
                row = dict(var=v, codec=name, error=f"{type(e).__name__}: {str(e)[:160]}")
            print({k: row[k] for k in row if k != "config"}, flush=True)
            rows.append(row)
    except Exception:  # noqa: BLE001
        rows.append(dict(var=v, error=traceback.format_exc()[-400:]))
    return rows


if __name__ == "__main__":
    with Pool(2) as pool:
        out = [r for rows in pool.imap_unordered(run_var, VARS) for r in rows]
    json.dump(out, open(HERE / "log04b.json", "w"), indent=1, default=str)
    print("DONE04b")
