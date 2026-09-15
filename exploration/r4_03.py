import json, lzma, inspect, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2, Delta
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_combinators.stack import CodecStack
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_wasm_sperr import Sperr
print("FramedCodecStack", inspect.signature(FramedCodecStack.__init__), flush=True)
da = h.load_03(); log = []
R = lambda n, f: h.run("03", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
QOI = "(X[I[0]-5] - X[I[0]+5]) / 357.5"
def sg(inner, eb=1e-6):
    return SafeguardedCodec(codec=inner, safeguards=[{"kind": "qoi_eb_stencil", "qoi": QOI,
        "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}], "type": "abs", "eb": eb}])
fso = lambda step=3.574e-4: FixedScaleOffset(offset=0, scale=1/step, dtype="<f8", astype="u1")
R("Framed(FSO step 3.574e-4 u1, lzma9e)", lambda: FramedCodecStack(fso(), LZMA(preset=E)))
R("Framed(FSO u1, Delta u1, lzma9e)", lambda: FramedCodecStack(fso(), Delta(dtype="u1"), LZMA(preset=E)))
R("Framed(FSO u1, bz2)", lambda: FramedCodecStack(fso(), BZ2(level=9)))
for q in [2.5e-4, 3.0e-4, 4.0e-4, 4.5e-4, 5.5e-4]:
    R(f"Safeguarded(Sperr q {q}) stencil", lambda q=q: sg(Sperr(mode="q", q=q)))
R("Safeguarded(Sperr q 3.5e-4) + lzma9e", lambda: CodecStack(sg(Sperr(mode="q", q=3.5e-4)), LZMA(preset=E)))
json.dump(log, open("log_r4_03.json", "w"), indent=1)
print("DONE r4_03")
