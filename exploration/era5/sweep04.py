import json, lzma, sys, time, contextlib, io, traceback
import numpy as np
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).parent
TIME = "2026-07-15T12:00:00"
VARS = ["cc", "ciwc", "clwc", "crwc", "cswc", "d", "o3", "pv", "q", "r", "t", "u", "v", "vo", "w", "z"]
E = 9 | lzma.PRESET_EXTREME


def load(v):
    p = HERE / "cache" / f"pressure_{v}.npy"
    if not p.exists():
        import era5_loader as L
        ds = L.load_era5_data(leveltype="pressure", param=v)
        np.save(p, ds[L._var_name(ds, v)].sel(time=TIME).values)
    return np.load(p)


def candidates(v, x):
    from numcodecs import LZMA, FixedScaleOffset
    from numcodecs_combinators.framed import FramedCodecStack
    from numcodecs_combinators.stack import CodecStack
    from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
    from numcodecs_wasm_sperr import Sperr
    from numcodecs_wasm_sz3 import Sz3
    from numcodecs_wasm_zstd import Zstd
    from numcodecs_zero import ZeroCodec

    def lz(delta):
        return LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": delta}, {"id": lzma.FILTER_LZMA2, "preset": E, "lc": 1, "lp": 1, "pb": 1}])

    def absq(eb):  # snap to a 2*eb grid, smallest integer type that fits
        step = 2 * eb * 0.9999
        span = max(abs(np.nanmin(x)), abs(np.nanmax(x))) / step + 2
        dt, size = ("<i1", 1) if span < 127 else ("<i2", 2) if span < 32767 else ("<i4", 4)
        return FramedCodecStack(FixedScaleOffset(offset=0, scale=1 / step, dtype="<f8", astype=dt), lz(size))

    def relq(ratio, frac=0.9999):  # quantise log2|x| on a 2*log2(ratio) grid
        step = 2 * np.log2(ratio) * frac
        inner = FixedScaleOffset(offset=0, scale=1 / step, dtype="<f8", astype="<i2").get_config()
        return CodecStack(PointwiseRatioErrorBoundedCodec(eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec=inner, sign_codec=Zstd(level=19)), lz(2))

    def relsz3(ratio):
        return PointwiseRatioErrorBoundedCodec(eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec={**Sz3(eb_mode="abs", eb_abs=1.0, predictor="lorenzo").get_config(), "eb_abs": "$eb_abs"}, sign_codec=Zstd(level=19))

    c = {"Zero": ZeroCodec}
    rel = {"cc": 1.01, "ciwc": 1.01, "clwc": 1.01, "crwc": 1.01, "cswc": 1.01, "o3": 1.01, "q": 1.01, "r": 1.01, "t": 1.01,
           "d": 1.05, "vo": 1.05, "w": 1.05, "pv": 1.1}
    ab = {"u": 0.5, "v": 0.5, "t": 0.05, "w": 0.01, "pv": 1e-7, "z": 10.0}
    if v in rel:
        r = rel[v]
        c[f"PWRatio(FSO log2 i2 r={r})+LZMA"] = lambda r=r: relq(r)
        c[f"PWRatio(Sz3 lorenzo r={r})"] = lambda r=r: relsz3(r)
        # ratio bound x/r..x*r keeps |err| <= (r-1)|x| only on the upper side; use r=1+eb exactly
    if v in ab:
        eb = ab[v]
        c[f"FSO grid 2*{eb}+LZMA"] = lambda eb=eb: absq(eb)
        c[f"Sz3 abs {eb}"] = lambda eb=eb: Sz3(eb_mode="abs", eb_abs=eb)
        c[f"Sperr pwe {eb}"] = lambda eb=eb: Sperr(mode="pwe", pwe=eb)
    if v == "z":  # mean abs 5 AND max abs 10: smaller grid steps keep the mean below 5
        for eb in [9.0, 8.0]:
            c[f"FSO grid 2*{eb}+LZMA"] = lambda eb=eb: absq(eb)
    return c


def run_var(v):
    from compression_recommendations import Recommendations
    from compression_requirement_checks import check_safety_requirements
    from compression_requirement_safeguards import safeguards_for_requirements
    from numcodecs_safeguards import SafeguardedCodec
    rows = []
    try:
        x = load(v)
        reqs = Recommendations.provide.search(markers={"grib-short-name": v, "level-kind": "pressure"})
        for name, make in candidates(v, x).items():
            for wrapped in (False, True):
                if name == "Zero" and not wrapped:
                    continue
                label = f"Safeguarded({name})" if wrapped else name
                try:
                    inner = make()
                    codec = SafeguardedCodec(codec=inner, safeguards=safeguards_for_requirements(*reqs)) if wrapped else inner
                    t = time.time()
                    enc = codec.encode(x)
                    dec = codec.decode(enc)
                    dec = np.asarray(dec).reshape(x.shape)
                    te = time.time() - t
                    with contextlib.redirect_stdout(io.StringIO()):
                        ok = bool(check_safety_requirements(original=x, reconstructed=dec, requirements=reqs))
                    row = dict(var=v, codec=label, cr=round(x.nbytes / np.array(enc).nbytes, 3), ok=ok, sec=round(te, 1), config=codec.get_config())
                except Exception as e:  # noqa: BLE001
                    row = dict(var=v, codec=label, error=f"{type(e).__name__}: {str(e)[:160]}")
                print({k: row[k] for k in row if k != "config"}, flush=True)
                rows.append(row)
    except Exception:
        rows.append(dict(var=v, error=traceback.format_exc()[-400:]))
        print(rows[-1], flush=True)
    return rows


if __name__ == "__main__":
    with Pool(4) as pool:
        out = [r for rows in pool.imap_unordered(run_var, VARS) for r in rows]
    json.dump(out, open(HERE / "log04.json", "w"), indent=1, default=str)
    best = {}
    for r in out:
        if r.get("ok") and r["cr"] > best.get(r["var"], {}).get("cr", 0):
            best[r["var"]] = r
    print("BEST04:")
    for v in VARS:
        b = best.get(v)
        print(f"  {v}: {b['cr']} {b['codec']}" if b else f"  {v}: none")
    print("DONE04")
