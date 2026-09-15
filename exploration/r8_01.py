import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA
from numcodecs.packbits import PackBits
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_replace import ReplaceFilterCodec
da = h.load_01(); log = []
R = lambda n, f: h.run("01", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
def lz(delta=None, lc=3, lp=0, pb=2):
    f = ([{"id": lzma.FILTER_DELTA, "dist": delta}] if delta else []) + [{"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": lp, "pb": pb}]
    return LZMA(format=lzma.FORMAT_RAW, filters=f)
def mask(inner, fill="finite_mean"):
    return MaskMetaCodec(mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: fill}), *inner),
                         bitmap_codec=CodecStack(PackBits(), LZMA(preset=E)))
fso = lambda: FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="u1")
for lc in []:
    for pb in [0, 2]:
        R(f"Mask FSO u1 + lzma delta1 lc{lc} pb{pb}", lambda lc=lc, pb=pb: mask([fso(), lz(1, lc, 0, pb)]))
for fill, lc in [(f, l) for f in [6.0, 10.0, 14.0, 18.0, 22.0, 26.0, 30.0] for l in (2, 4)]:
    R(f"Mask(fill={fill}) FSO u1 + lzma delta1 lc{lc} pb0", lambda fill=fill, lc=lc: mask([fso(), lz(1, lc, 0, 0)], fill))
json.dump(log, open("log_r8_01.json", "w"), indent=1)
print("DONE r8_01")
