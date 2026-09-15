import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA
from numcodecs.packbits import PackBits
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_wasm_pco import Pco
from numcodecs_wasm_zstd import Zstd
try: Pco(delta="auto", level=8, mode="auto", paging="???")
except Exception as e: print("PAGING OPTIONS:", str(e)[:400], flush=True)
E = 9 | lzma.PRESET_EXTREME
PAGING = "equal-pages-up-to"
def pco(delta="auto", order=None, level=12, mode="auto"):
    kw = dict(delta=delta, level=level, mode=mode, paging=PAGING)
    if order is not None: kw["delta_encoding_order"] = order
    return Pco(**kw)
VARIANTS = {"auto": lambda: pco(), "consec1": lambda: pco("try-consecutive", 1), "consec2": lambda: pco("try-consecutive", 2),
            "lookback": lambda: pco("try-lookback"), "conv1 o2": lambda: pco("try-conv1", 2), "classic noop": lambda: pco("no-op", mode="classic")}
log = []
# 01: masked step-2 grid, u2 bins
da = h.load_01()
for n, p in VARIANTS.items():
    h.run("01", f"Mask(fill20) FSO u2 + Pco {n}", lambda p=p: MaskMetaCodec(mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: 20.0}), FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="<u2"), p()), bitmap_codec=CodecStack(PackBits(), LZMA(preset=E))), da, log)
# 02: log2 grid inside PWRatio, pco as the log codec's backend
da = h.load_02(); EB = np.log2(1.01)
for n, p in VARIANTS.items():
    h.run("02", f"PWRatio(Stack(FSO log2 i2, Pco {n}))", lambda p=p: PointwiseRatioErrorBoundedCodec(eb_ratio=1.01, eb_abs_marker="$eb_abs", log_codec=CodecStack(FixedScaleOffset(offset=0, scale=1 / (2 * EB * 0.9999), dtype="<f8", astype="<i2"), p()).get_config(), sign_codec=Zstd(level=19)), da, log)
# 03: pointwise grid 2*1.7874e-4, i2 bins
da = h.load_03()
for n, p in VARIANTS.items():
    h.run("03", f"Framed(FSO i2 step 3.5748e-4, Pco {n})", lambda p=p: FramedCodecStack(FixedScaleOffset(offset=0, scale=1 / 3.5748e-4, dtype="<f8", astype="<i2"), p()), da, log)
json.dump(log, open("log_r9_pco.json", "w"), indent=1)
print("DONE r9")
