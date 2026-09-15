import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2, Delta, Shuffle
from numcodecs_combinators.stack import CodecStack
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_wasm_zstd import Zstd
da = h.load_02(); log = []
R = lambda n, f: h.run("02", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
EB = np.log2(1.01)
FRAC = 0.9999
def fso(dtype="<i2", off=0.0):
    return FixedScaleOffset(offset=off, scale=1 / (2 * EB * FRAC), dtype="<f8", astype=dtype)
def pw(inner):
    cfg = inner.get_config() if hasattr(inner, "get_config") else inner
    return PointwiseRatioErrorBoundedCodec(eb_ratio=1.01, eb_abs_marker="$eb_abs", log_codec=cfg, sign_codec=Zstd(level=19))
def lz(delta=None, lc=3, lp=0, pb=2):
    f = ([{"id": lzma.FILTER_DELTA, "dist": delta}] if delta else []) + [{"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": lp, "pb": pb}]
    return LZMA(format=lzma.FORMAT_RAW, filters=f)
R("ref: PW(FSO i2) + lzma delta2", lambda: CodecStack(pw(fso()), LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": 2}, {"id": lzma.FILTER_LZMA2, "preset": E}])))
for lc, lp, pb in [(0,1,1), (1,1,1), (3,1,1), (0,0,0), (8,1,1)]:
    R(f"PW(FSO i2) + raw lzma delta2 lc{lc} lp{lp} pb{pb}", lambda lc=lc, lp=lp, pb=pb: CodecStack(pw(fso()), lz(2, lc, lp, pb)))
R("PW(Stack(FSO i2, Delta i2)) + lzma9e", lambda: CodecStack(pw(CodecStack(fso(), Delta(dtype="<i2"))), lz()))
R("PW(Stack(FSO i2, Delta i2)) + lzma lc0 lp1 pb1", lambda: CodecStack(pw(CodecStack(fso(), Delta(dtype="<i2"))), lz(None, 0, 1, 1)))
R("PW(Stack(FSO i2, Delta i2, Shuffle2)) + lzma9e", lambda: CodecStack(pw(CodecStack(fso(), Delta(dtype="<i2"), Shuffle(elementsize=2))), lz()))
R("PW(FSO i2) + Shuffle? n/a -> lzma delta4", lambda: CodecStack(pw(fso()), lz(4)))
R("PW(FSO i2 offset half-step) + lzma delta2", lambda: CodecStack(pw(fso(off=EB * FRAC)), lz(2)))
json.dump(log, open("log_r5_02.json", "w"), indent=1)
print("DONE r5_02")
