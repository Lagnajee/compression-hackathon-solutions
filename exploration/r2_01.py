import json, itertools, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2
from numcodecs.packbits import PackBits
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_wasm_zstd import Zstd
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_lc import Lc
from numcodecs_wasm_bit_round import BitRound
import lzma
da = h.load_01(); log = []
def R(n, f, quiet=False):
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): row = h.run("01", n, f, da, log)
    if not quiet: print(row, flush=True)
BM = {"zstd19": lambda: CodecStack(PackBits(), Zstd(level=19)), "lzma9e": lambda: CodecStack(PackBits(), LZMA(preset=9 | lzma.PRESET_EXTREME))}
def mask(inner, fill="finite_mean", bm="zstd19"):
    return MaskMetaCodec(mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: fill}), *inner), bitmap_codec=BM[bm]())
FSO = lambda: FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="u1")
BACK = {"zstd22": lambda: [Zstd(level=22)], "lzma9e": lambda: [LZMA(preset=9 | lzma.PRESET_EXTREME)], "bz2": lambda: [BZ2(level=9)],
        "lc DIFFMS1 RZE1": lambda: [Lc(components=[{"id":"DIFFMS","size":1},{"id":"RZE","size":1}])]}
for fill in ["finite_mean", 0.0]:
    for bm in BM:
        for bk, b in BACK.items():
            R(f"Mask(fill={fill},bm={bm}) FSO step2 u1 + {bk}", lambda fill=fill, bm=bm, b=b: mask([FSO(), *b()], fill, bm))
R("Mask Sz3 abs1 interp-lorenzo", lambda: mask([Sz3(eb_mode="abs", eb_abs=1.0)]))
R("Mask Sz3 abs1 interp-lorenzo fill0", lambda: mask([Sz3(eb_mode="abs", eb_abs=1.0)], 0.0))
R("Mask BitRound abs1 + zstd22", lambda: mask([BitRound(mode="abs", eb_abs=1.0), Zstd(level=22)]))
R("Mask BitRound abs1 + lzma9e", lambda: mask([BitRound(mode="abs", eb_abs=1.0), LZMA(preset=9 | lzma.PRESET_EXTREME)]))
# LC pipeline grid on masked QUANT ABS
A = [("DIFFMS",4),("DIFFNB",4),("TCMS",4),("TCNB",4),("BIT",4)]
B = [(c,s) for c in ["RLE","RRE","RZE","RARE","RAZE","CLOG","HCLOG"] for s in (1,4)]
pipes = [[b] for b in B] + [[a,b] for a in A for b in B] + [[a1,a2,b] for a1 in A for a2 in A if a1!=a2 for b in B]
for p in pipes:
    comps = [{"id":c,"size":s} for c,s in p]
    R("Mask LC ABS1 " + " ".join(f"{c}{s}" for c,s in p), lambda comps=comps: mask([Lc(preprocessors=[{"id":"QUANT","dtype":"f32","kind":"ABS","error_bound":1.0,"decorrelation":"0"}], components=comps)]), quiet=True)
json.dump(log, open("log_r2_01.json", "w"), indent=1)
ok = sorted([r for r in log if r.get("ok")], key=lambda r: -r["cr"])
print("TOP01:"); [print(r) for r in ok[:15]]
print("DONE r2_01")
