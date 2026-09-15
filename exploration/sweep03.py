import json, numpy as np, harness as h
from numcodecs_combinators.stack import CodecStack
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_zero import ZeroCodec
from numcodecs_wasm_zstd import Zstd
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_zfp import Zfp
from numcodecs_wasm_sperr import Sperr
from numcodecs_wasm_lc import Lc
from numcodecs_wasm_bit_round import BitRound
da = h.load_03(); log = []
R = lambda n, f: h.run("03", n, f, da, log)
QOI = "(X[I[0]-5] - X[I[0]+5]) / 357.5"
def sg(inner, eb=1e-6):
    return SafeguardedCodec(codec=inner, safeguards=[{"kind": "qoi_eb_stencil", "qoi": QOI,
        "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}], "type": "abs", "eb": eb}])
R("Sperr psnr25 (notebook default)", lambda: Sperr(mode="psnr", psnr=25))
for eb in [1.78e-4, 1.7e-4]:
    for p in ["interpolation-lorenzo", "interpolation", "lorenzo"]:
        R(f"Sz3 abs {eb} {p}", lambda eb=eb, p=p: Sz3(eb_mode="abs", eb_abs=eb, predictor=p))
    R(f"Zfp tol {eb}", lambda eb=eb: Zfp(mode="fixed-accuracy", tolerance=eb))
    R(f"Sperr pwe {eb}", lambda eb=eb: Sperr(mode="pwe", pwe=eb))
    R(f"BitRound abs {eb} + Zstd19", lambda eb=eb: CodecStack(BitRound(mode="abs", eb_abs=eb), Zstd(level=19)))
    R(f"Lc ABS {eb} BIT RLE", lambda eb=eb: Lc(preprocessors=[{"id":"QUANT","dtype":"f64","kind":"ABS","error_bound":eb,"decorrelation":"0"}], components=[{"id":"BIT","size":8},{"id":"RLE","size":8}]))
for t in [3.5e-4, 1e-3]:
    R(f"Zfp tol {t} (unsafeguarded)", lambda t=t: Zfp(mode="fixed-accuracy", tolerance=t))
    R(f"Sperr pwe {t} (unsafeguarded)", lambda t=t: Sperr(mode="pwe", pwe=t))
R("Safeguarded(Zero) stencil", lambda: sg(ZeroCodec()))
for eb in [1.78e-4, 3.5e-4, 7e-4]:
    R(f"Safeguarded(Sz3 abs {eb}) stencil", lambda eb=eb: sg(Sz3(eb_mode="abs", eb_abs=eb)))
for t in [3.5e-4, 1e-3]:
    R(f"Safeguarded(Sperr pwe {t}) stencil", lambda t=t: sg(Sperr(mode="pwe", pwe=t)))
    R(f"Safeguarded(Zfp tol {t}) stencil", lambda t=t: sg(Zfp(mode="fixed-accuracy", tolerance=t)))
json.dump(log, open("log03.json", "w"), indent=1)
print("DONE03")
