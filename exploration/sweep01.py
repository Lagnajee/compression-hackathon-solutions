import json, numpy as np, harness as h
from numcodecs.packbits import PackBits
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_wasm_zstd import Zstd
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_zfp import Zfp
from numcodecs_wasm_sperr import Sperr
from numcodecs_wasm_ebcc import Ebcc
from numcodecs_wasm_lc import Lc
from numcodecs_wasm_bit_round import BitRound
try: Lc(components=[{"id": "???"}])
except Exception as e: print("LC components:", str(e)[:1500])
da = h.load_01(); log = []
bm = lambda: CodecStack(PackBits(), Zstd(level=19))
def nanmask(inner):
    return MaskMetaCodec(mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: "finite_mean"}), inner), bitmap_codec=bm())
def sg(inner, eb=1.0):
    return SafeguardedCodec(codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: "finite_mean"}), inner), safeguards=[{"kind": "eb", "type": "abs", "eb": eb}])
R = lambda n, f: h.run("01", n, f, da, log)
R("Zfp tol1 allow-unsafe (notebook default)", lambda: Zfp(mode="fixed-accuracy", tolerance=1, non_finite="allow-unsafe"))
for eb in [1.0, 0.999, 0.99]:
    for p in ["interpolation-lorenzo", "interpolation", "lorenzo", "lorenzo-regression"]:
        R(f"Sz3 abs {eb} {p}", lambda eb=eb, p=p: Sz3(eb_mode="abs", eb_abs=eb, predictor=p))
R("BitRound abs1 + Zstd19", lambda: CodecStack(BitRound(mode="abs", eb_abs=1.0), Zstd(level=19)))
R("Lc QUANT ABS f32 1 BIT RLE", lambda: Lc(preprocessors=[{"id":"QUANT","dtype":"f32","kind":"ABS","error_bound":1.0,"decorrelation":"0"}], components=[{"id":"BIT","size":4},{"id":"RLE","size":4}]))
for t in [1, 2, 3]:
    R(f"Mask+Zfp tol{t}", lambda t=t: nanmask(Zfp(mode="fixed-accuracy", tolerance=t)))
R("Mask+Sperr pwe1", lambda: nanmask(Sperr(mode="pwe", pwe=1.0)))
R("Mask+Ebcc abs1", lambda: nanmask(Ebcc(base_cr=100, residual="absolute", error=1.0)))
R("Safeguarded(Sz3 abs1) eb1", lambda: sg(Sz3(eb_mode="abs", eb_abs=1.0)))
for t in [2, 4]:
    R(f"Safeguarded(Zfp tol{t}) eb1", lambda t=t: sg(Zfp(mode="fixed-accuracy", tolerance=t)))
R("Safeguarded(Sperr pwe1.5) eb1", lambda: sg(Sperr(mode="pwe", pwe=1.5)))
json.dump(log, open("log01.json", "w"), indent=1)
print("DONE01")
