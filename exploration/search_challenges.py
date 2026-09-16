"""Search for stronger codecs for challenges 01-03, scored by each notebook's own check.

Families are evaluated over a geometric grid of a looseness parameter `p`. A
candidate counts only if the challenge reports zero violations. Results are
logged to `exploration/logs_challenges_<key>.json`.

    uv run python exploration/search_challenges.py <01|02|03>
"""

import json
import lzma
import sys
import time
from pathlib import Path

import numpy as np
from numcodecs import LZMA, BZ2, Delta, FixedScaleOffset
from numcodecs.packbits import PackBits
from numcodecs_bitmap_index import BitmapIndexCodec
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_combinators.stack import CodecStack
from numcodecs_delta import BinaryDeltaCodec
from numcodecs_mask import MaskMetaCodec
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_shuffle import TypedByteShuffleCodec
from numcodecs_tokenize import TokenizeCodec
from numcodecs_wasm_round import Round
from numcodecs_wasm_sperr import Sperr
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_zfp import Zfp
from numcodecs_wasm_zstd import Zstd

import hackathon  # noqa: F401
from hackathon.challenges import CHALLENGES

ROOT = Path(__file__).resolve().parents[1]
E = 9 | lzma.PRESET_EXTREME
LZ = lambda: LZMA(preset=E)
RAWLZ = lambda delta=None, lc=3, lp=0, pb=2: LZMA(
    format=lzma.FORMAT_RAW,
    filters=([{"id": lzma.FILTER_DELTA, "dist": delta}] if delta else [])
    + [{"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": lp, "pb": pb}],
)
GRID = (0.5, 0.71, 1.0, 1.41, 2.0, 2.83, 4.0, 5.66, 8.0, 11.3, 16.0)


def candidates_01():
    """|err| <= 1 and NaNs preserved. Step-2 rounding is optimal; vary the lossless tail."""
    c = {"current: Round2+Tokenize+rawLZMA(lc4,pb0)": lambda: FramedCodecStack(Round(precision=2.0), TokenizeCodec(), RAWLZ(None, 4, 0, 0))}
    tails = {
        "Tokenize+BitmapIndex+Shuffle+LZMA": [TokenizeCodec(), BitmapIndexCodec(), TypedByteShuffleCodec(), LZ()],
        "Tokenize+BitmapIndex+LZMA": [TokenizeCodec(), BitmapIndexCodec(), LZ()],
        "Tokenize+Delta(u1)+rawLZMA(lc4,pb0)": [TokenizeCodec(), Delta(dtype="u1"), RAWLZ(None, 4, 0, 0)],
        "Tokenize+BinaryDelta+LZMA": [TokenizeCodec(), BinaryDeltaCodec(), LZ()],
        "Tokenize+BZ2": [TokenizeCodec(), BZ2(level=9)],
        "Tokenize+Zstd22": [TokenizeCodec(), Zstd(level=22)],
        "BitmapIndex+LZMA (no tokenize)": [BitmapIndexCodec(), LZ()],
        "Tokenize+rawLZMA(lc0,pb0)": [TokenizeCodec(), RAWLZ(None, 0, 0, 0)],
        "Tokenize+rawLZMA(delta1,lc4,pb0)": [TokenizeCodec(), RAWLZ(1, 4, 0, 0)],
    }
    for name, tail in tails.items():
        c[f"Round2+{name}"] = lambda tail=tail: FramedCodecStack(Round(precision=2.0), *tail)
    # mask NaNs first, then an integer grid (the previous runner-up), with new tails
    for name, tail in [("BitmapIndex+Shuffle+LZMA", [BitmapIndexCodec(), TypedByteShuffleCodec(), LZ()]), ("rawLZMA(delta1,lc4,pb0)", [RAWLZ(1, 4, 0, 0)])]:
        c[f"Mask+fill20+FSO(u1)+{name}"] = lambda tail=tail: MaskMetaCodec(
            mask=np.nan,
            codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: 20.0}), FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="u1"), *tail),
            bitmap_codec=CodecStack(PackBits(), LZ()),
        )
    return {k: (v, None) for k, v in c.items()}


def candidates_02():
    """|err| <= 1% of |value|. Push the inner codec past 1% and let the rel safeguard fix it."""
    eb = 0.01
    step = 2 * np.log2(1 + eb) * 0.9999
    sg = [{"kind": "eb", "type": "rel", "eb": eb}]
    fso = lambda p: FixedScaleOffset(offset=0, scale=1 / (step * p), dtype="<f8", astype="<i2").get_config()
    sz3 = Sz3(eb_mode="abs", eb_abs=1.0).get_config()
    sperr = Sperr(mode="pwe", pwe=1.0).get_config()

    def pw(cfg, key, ratio):
        return PointwiseRatioErrorBoundedCodec(eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec={**cfg, key: "$eb_abs"}, sign_codec=Zstd(level=19))

    c = {"current: PwRatio(FSO log i2)+rawLZMA(delta2)": (lambda: CodecStack(PointwiseRatioErrorBoundedCodec(eb_ratio=1.01, eb_abs_marker="$eb_abs", log_codec=fso(1.0), sign_codec=Zstd(level=19)), RAWLZ(2, 1, 1, 1)), None)}
    for tag, inner in (("SPERR", lambda p: pw(sperr, "pwe", (1 + eb) ** p)), ("SZ3", lambda p: pw(sz3, "eb_abs", (1 + eb) ** p))):
        c[f"Safeguarded(rel)(PwRatio({tag}))+LZMA"] = (lambda p, inner=inner: CodecStack(SafeguardedCodec(codec=inner(p), safeguards=sg), LZ()), GRID)
        c[f"PwRatio({tag}) unsafeguarded+LZMA"] = (lambda p, inner=inner: CodecStack(inner(p), LZ()), GRID)
    c["Safeguarded(rel)(PwRatio(FSO log i2))+rawLZMA(delta2)"] = (
        lambda p: CodecStack(SafeguardedCodec(codec=PointwiseRatioErrorBoundedCodec(eb_ratio=(1 + eb) ** p, eb_abs_marker="$eb_abs", log_codec=fso(p), sign_codec=Zstd(level=19)), safeguards=sg), RAWLZ(2, 1, 1, 1)), GRID)
    return c


def candidates_03():
    """|err of the longitude gradient| <= 1e-6, enforced by the stencil QoI safeguard."""
    qoi = [{"kind": "qoi_eb_stencil", "qoi": "(X[I[0]-5] - X[I[0]+5]) / 357.5",
            "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}], "type": "abs", "eb": 1e-6}]
    base_q, base_pwe, base_grid = 4.25e-4, 1.7875e-4, 3.574e-4
    sg = lambda inner: SafeguardedCodec(codec=inner, safeguards=qoi)
    c = {"current: Safeguarded(qoi)(SPERR q 4.25e-4)+LZMA": (lambda: CodecStack(sg(Sperr(mode="q", q=base_q)), LZ()), None)}
    c["Safeguarded(qoi)(SPERR q)+LZMA"] = (lambda p: CodecStack(sg(Sperr(mode="q", q=p * base_q)), LZ()), (0.71, 0.84, 1.0, 1.19, 1.41, 2.0))
    c["Safeguarded(qoi)(SPERR pwe)+LZMA"] = (lambda p: CodecStack(sg(Sperr(mode="pwe", pwe=p * base_pwe)), LZ()), (1.0, 1.41, 2.0, 2.83, 4.0))
    c["Safeguarded(qoi)(SZ3 abs)+LZMA"] = (lambda p: CodecStack(sg(Sz3(eb_mode="abs", eb_abs=p * base_pwe)), LZ()), (1.0, 2.0, 4.0))
    c["Safeguarded(qoi)(ZFP acc)+LZMA"] = (lambda p: CodecStack(sg(Zfp(mode="fixed-accuracy", tolerance=p * base_pwe)), LZ()), (1.0, 2.0, 4.0))
    c["Safeguarded(qoi)(FSO grid i2)+LZMA"] = (lambda p: CodecStack(sg(FramedCodecStack(FixedScaleOffset(offset=0, scale=1 / (p * base_grid), dtype="<f8", astype="<i2"), RAWLZ(2, 1, 1, 1))), LZ()), (1.0, 2.0, 4.0))
    c["Safeguarded(qoi, LZMA corrections)(SPERR q)+LZMA"] = (
        lambda p: CodecStack(SafeguardedCodec(codec=Sperr(mode="q", q=p * base_q), safeguards=qoi,
                                              lossless={"for_codec": None, "for_corrections": FramedCodecStack(LZ()).get_config()}), LZ()),
        (1.0, 1.41, 2.0))
    return c


def main():
    key = sys.argv[1]
    challenge = {"01": "01-nan-missing-values", "02": "02-relative-error-bound", "03": "03-spatial-gradient"}[key]
    ch = CHALLENGES[challenge]
    da = ch.load()
    cands = {"01": candidates_01, "02": candidates_02, "03": candidates_03}[key]()
    log = []
    for name, (build, grid) in cands.items():
        for p in (grid or [None]):
            label = name if p is None else f"{name} p={p:g}"
            try:
                codec = build() if p is None else build(p)
                t = time.time()
                res = ch.evaluate(codec, da)
                row = dict(name=label, cr=round(res.compression_ratio, 3), violations=res.violations, ok=res.ok, sec=round(time.time() - t, 1), config=codec.get_config())
            except Exception as e:  # noqa: BLE001
                row = dict(name=label, error=f"{type(e).__name__}: {str(e)[:150]}")
            print({k: row[k] for k in row if k != "config"}, flush=True)
            log.append(row)
    (ROOT / "exploration" / f"logs_challenges_{key}.json").write_text(json.dumps(log, indent=1, default=str))
    ok = sorted((r for r in log if r.get("ok")), key=lambda r: -r["cr"])
    print(f"TOP {key}:", [(r["cr"], r["name"]) for r in ok[:5]])


if __name__ == "__main__":
    main()
