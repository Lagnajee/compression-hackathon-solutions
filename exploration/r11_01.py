import inspect, json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_safeguards import SafeguardedCodec
print("SafeguardedCodec", inspect.signature(SafeguardedCodec.__init__), flush=True)
da = h.load_01(); log = []
R = lambda n, f: h.run("01", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
def lz():
    return LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": 1}, {"id": lzma.FILTER_LZMA2, "preset": E, "lc": 4, "lp": 0, "pb": 0}])
def inner(s, astype):
    return FramedCodecStack(ReplaceFilterCodec(replacements={np.nan: s}), FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype=astype), lz())
SG = [{"kind": "eb", "type": "abs", "eb": 1.0, "equal_nan": True}]
for s, astype in [(20.0, "<u1"), (0.0, "<u1"), (-2.0, "<i1"), (-178.0, "<i1")]:
    R(f"Safeguarded(Framed(nan->{s}, FSO {astype}, LZMA)) eb1", lambda s=s, astype=astype: SafeguardedCodec(codec=inner(s, astype), safeguards=SG))
    R(f"Safeguarded(Framed(nan->{s}, FSO {astype}, LZMA)) eb1 + LZMA corrections", lambda s=s, astype=astype: SafeguardedCodec(codec=inner(s, astype), safeguards=SG, lossless={"for_codec": None, "for_corrections": FramedCodecStack(LZMA(preset=E)).get_config()}))
json.dump(log, open("log_r11_01.json", "w"), indent=1)
print("DONE r11")
