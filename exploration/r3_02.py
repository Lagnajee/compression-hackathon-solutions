import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2, Delta
from numcodecs_combinators.stack import CodecStack
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_wasm_zstd import Zstd
from numcodecs_wasm_sz3 import Sz3
da = h.load_02(); log = []
R = lambda n, f: h.run("02", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
EB = np.log2(1.01)
def pwq(step_frac, dtype="<i2", delta=False):
    step = 2 * EB * step_frac
    inner = FixedScaleOffset(offset=0, scale=1 / step, dtype="<f8", astype=dtype).get_config()
    return PointwiseRatioErrorBoundedCodec(eb_ratio=1.01, eb_abs_marker="$eb_abs", log_codec=inner, sign_codec=Zstd(level=19))
R("PWRatio(Sz3 lorenzo) + lzma9e", lambda: CodecStack(PointwiseRatioErrorBoundedCodec(eb_ratio=1.01, eb_abs_marker="$eb_abs", log_codec={**Sz3(eb_mode="abs", eb_abs=1.0, predictor="lorenzo").get_config(), "eb_abs": "$eb_abs"}, sign_codec=Zstd(level=19)), LZMA(preset=E)))
for frac in [0.999999, 0.9999]:
    R(f"PWRatio(FSO log2 step {frac}*2eb i2) + lzma9e", lambda frac=frac: CodecStack(pwq(frac), LZMA(preset=E)))
    R(f"PWRatio(FSO log2 step {frac}*2eb i2) + bz2", lambda frac=frac: CodecStack(pwq(frac), BZ2(level=9)))
    R(f"PWRatio(FSO log2 step {frac}*2eb i2) + zstd22", lambda frac=frac: CodecStack(pwq(frac), Zstd(level=22)))
    R(f"PWRatio(FSO log2 step {frac}*2eb i2) + lzma delta2", lambda frac=frac: CodecStack(pwq(frac), LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_DELTA, "dist": 2}, {"id": lzma.FILTER_LZMA2, "preset": E}])))
json.dump(log, open("log_r3_02.json", "w"), indent=1)
print("DONE r3_02")
