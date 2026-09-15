import json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2, Delta
from numcodecs_combinators.stack import CodecStack
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_sperr import Sperr
da = h.load_03(); log = []
R = lambda n, f: h.run("03", n, f, da, log)
QOI = "(X[I[0]-5] - X[I[0]+5]) / 357.5"
def sg(inner, eb=1e-6):
    return SafeguardedCodec(codec=inner, safeguards=[{"kind": "qoi_eb_stencil", "qoi": QOI,
        "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}], "type": "abs", "eb": eb}])
L = lambda: LZMA(preset=9 | lzma.PRESET_EXTREME)
R("Sperr pwe 1.7875e-4 + lzma9e", lambda: CodecStack(Sperr(mode="pwe", pwe=1.7875e-4), L()))
for step in [3.57e-4, 3.574e-4]:
    fso = lambda step=step: FixedScaleOffset(offset=0, scale=1/step, dtype="<f8", astype="u1")
    R(f"FSO step {step} u1 + lzma9e", lambda fso=fso: CodecStack(fso(), L()))
    R(f"FSO step {step} u1 + bz2", lambda fso=fso: CodecStack(fso(), BZ2(level=9)))
    R(f"FSO step {step} u1 + Delta + lzma9e", lambda fso=fso: CodecStack(fso(), Delta(dtype="u1"), L()))
for pwe in [2.0e-4, 2.3e-4, 2.6e-4]:
    R(f"Safeguarded(Sperr pwe {pwe}) stencil", lambda pwe=pwe: sg(Sperr(mode="pwe", pwe=pwe)))
for q in [3.5e-4, 7e-4, 1.4e-3]:
    R(f"Safeguarded(Sperr q {q}) stencil", lambda q=q: sg(Sperr(mode="q", q=q)))
json.dump(log, open("log_r3_03.json", "w"), indent=1)
print("DONE r3_03")
