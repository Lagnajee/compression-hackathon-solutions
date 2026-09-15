import json, lzma, harness as h
from numcodecs import LZMA
from numcodecs_combinators.stack import CodecStack
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_wasm_sperr import Sperr
da = h.load_03(); log = []
R = lambda n, f: h.run("03", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
QOI = "(X[I[0]-5] - X[I[0]+5]) / 357.5"
def sg(inner, eb=1e-6):
    return SafeguardedCodec(codec=inner, safeguards=[{"kind": "qoi_eb_stencil", "qoi": QOI,
        "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}], "type": "abs", "eb": eb}])
for q in [3.75e-4, 4.0e-4, 4.25e-4]:
    R(f"Safeguarded(Sperr q {q}) + lzma9e", lambda q=q: CodecStack(sg(Sperr(mode="q", q=q)), LZMA(preset=E)))
json.dump(log, open("log_r7_03.json", "w"), indent=1)
print("DONE r7_03")
