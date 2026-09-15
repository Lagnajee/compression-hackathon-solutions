import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA
from numcodecs.packbits import PackBits
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_safeguards import SafeguardedCodec
da = h.load_01(); log = []
R = lambda n, f: h.run("01", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
x = da.values
# how much of the current best is the NaN bitmap?
bm = np.array(CodecStack(PackBits(), LZMA(preset=E)).encode(np.isnan(x))).nbytes
print(f"bitmap bytes {bm}, raw {x.nbytes}, best total ~{x.nbytes/39.762:.0f} -> bitmap share {bm/(x.nbytes/39.762):.1%}", flush=True)
def lz(lc=4, pb=0):
    return LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": 1}, {"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": 0, "pb": pb}])
# sentinel fill -> its own grid level; the eb safeguard restores NaNs via corrections
for s in [20.0, 0.0, -2.0, -178.0]:
    astype = "<u1" if s >= 0 else "<i1" if s > -250 else "<i2"
    if s == -178.0: astype = "<i1"
    inner = lambda s=s, astype=astype: CodecStack(ReplaceFilterCodec(replacements={np.nan: s}), FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype=astype), lz())
    R(f"Safeguarded(Replace nan->{s}, FSO {astype}, LZMA) eb1", lambda inner=inner: SafeguardedCodec(codec=inner(), safeguards=[{"kind": "eb", "type": "abs", "eb": 1.0, "equal_nan": True}]))
# same, but corrections compressed with LZMA instead of the default pipeline
inner = lambda: CodecStack(ReplaceFilterCodec(replacements={np.nan: 20.0}), FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="<u1"), lz())
try:
    R("Safeguarded(fill20 FSO LZMA) eb1 + LZMA corrections", lambda: SafeguardedCodec(codec=inner(), safeguards=[{"kind": "eb", "type": "abs", "eb": 1.0, "equal_nan": True}], lossless_for_corrections=LZMA(preset=E)))
except Exception as e:
    print("lossless kw err", e)
json.dump(log, open("log_r10_01.json", "w"), indent=1)
print("DONE r10")
