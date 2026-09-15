import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2, Delta
from numcodecs.packbits import PackBits
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_replace import ReplaceFilterCodec
da = h.load_01(); log = []
R = lambda n, f: h.run("01", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
def lz(lc=3, lp=0, pb=2, delta=None):
    f = ([{"id": lzma.FILTER_DELTA, "dist": delta}] if delta else []) + [{"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": lp, "pb": pb}]
    return LZMA(format=lzma.FORMAT_RAW, filters=f)
def mask(inner, fill="finite_mean", bm=None):
    return MaskMetaCodec(mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: fill}), *inner),
                         bitmap_codec=bm or CodecStack(PackBits(), LZMA(preset=E)))
fso = lambda off=0.0: FixedScaleOffset(offset=off, scale=0.5, dtype="<f4", astype="u1")
R("baseline Mask FSO u1 + lzma9e", lambda: mask([fso(), LZMA(preset=E)]))
R("raw lzma9e (no container)", lambda: mask([fso(), lz()]))
for off in [0.5, 1.0, 1.5]:
    R(f"offset {off}", lambda off=off: mask([fso(off), LZMA(preset=E)]))
for lc in [0, 1, 2, 4]:
    for pb in [0, 2]:
        R(f"raw lzma lc{lc} pb{pb}", lambda lc=lc, pb=pb: mask([fso(), lz(lc=lc, pb=pb)]))
R("raw lzma delta1", lambda: mask([fso(), lz(delta=1)]))
R("numcodecs Delta u1 + lzma9e", lambda: mask([fso(), Delta(dtype="u1"), LZMA(preset=E)]))
R("fill 0 raw lzma", lambda: mask([fso(), lz()], 0.0))
R("bitmap raw lzma lc0", lambda: mask([fso(), lz()], bm=CodecStack(PackBits(), lz(lc=0, pb=0))))
json.dump(log, open("log_r3_01.json", "w"), indent=1)
print("DONE r3_01")
