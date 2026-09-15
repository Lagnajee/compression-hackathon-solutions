import json, lzma, numpy as np, harness as h
from numcodecs import LZMA
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_tokenize import TokenizeCodec
from numcodecs_wasm_round import Round
da = h.load_01(); log = []
R = lambda n, f: h.run("01", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
enc = TokenizeCodec().encode(Round(precision=2.0).encode(da.values))
print("token stream dtype", np.asarray(enc).dtype, "size", np.asarray(enc).size, flush=True)
for lc in [0, 1, 2, 3, 4]:
    for lp, pb in [(0, 0), (0, 2), (1, 1)]:
        R(f"Framed(Round 2, Tokenize, raw LZMA lc{lc} lp{lp} pb{pb})", lambda lc=lc, lp=lp, pb=pb: FramedCodecStack(Round(precision=2.0), TokenizeCodec(), LZMA(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": lp, "pb": pb}])))
ok = sorted([r for r in log if r.get("ok")], key=lambda r: -r["cr"])
json.dump(log, open("log_r13_01.json", "w"), indent=1)
print("TOP:", ok[:3]); print("DONE r13")
