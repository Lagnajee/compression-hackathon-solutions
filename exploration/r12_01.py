import inspect, json, lzma, numpy as np, harness as h
from numcodecs import FixedScaleOffset, LZMA, BZ2
from numcodecs.packbits import PackBits
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_tokenize import TokenizeCodec
from numcodecs_wasm_bit_round import BitRound
from numcodecs_wasm_round import Round
print("Round", inspect.signature(Round.__init__), (Round.__doc__ or "")[:300].replace("\n", " "), flush=True)
print("Tokenize", inspect.signature(TokenizeCodec.__init__), flush=True)
da = h.load_01(); log = []
R = lambda n, f: h.run("01", n, f, da, log)
E = 9 | lzma.PRESET_EXTREME
def lz(delta=1, lc=4, pb=0):
    f = ([{"id": lzma.FILTER_DELTA, "dist": delta}] if delta else []) + [{"id": lzma.FILTER_LZMA2, "preset": E, "lc": lc, "lp": 0, "pb": pb}]
    return LZMA(format=lzma.FORMAT_RAW, filters=f)
# current best for reference
best = lambda bm: MaskMetaCodec(mask=np.nan, codec=CodecStack(ReplaceFilterCodec(replacements={np.nan: 20.0}), FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="u1"), lz()), bitmap_codec=bm)
R("best: bitmap PackBits+LZMA", lambda: best(CodecStack(PackBits(), LZMA(preset=E))))
# cheaper bitmap: bool bytes straight into LZMA / BZ2
R("bitmap bool bytes + LZMA9e", lambda: best(LZMA(preset=E)))
R("bitmap bool bytes + raw LZMA lc0 pb0", lambda: best(lz(None, 0, 0)))
R("bitmap bool bytes + raw LZMA delta1 lc0", lambda: best(lz(1, 0, 0)))
R("bitmap bool bytes + BZ2", lambda: best(BZ2(level=9)))
R("bitmap PackBits + BZ2", lambda: best(CodecStack(PackBits(), BZ2(level=9))))
# NaN as a token: round in float space (keeps NaN), tokenize to uint8 indices, LZMA
for rname, rnd in [("BitRound abs1", lambda: BitRound(mode="abs", eb_abs=1.0)), ("Round precision=2", lambda: Round(precision=2.0))]:
    for lname, back in [("lz delta1 lc4 pb0", lambda: lz()), ("lz nodelta lc4 pb0", lambda: lz(None)), ("LZMA9e", lambda: LZMA(preset=E)), ("BZ2", lambda: BZ2(level=9))]:
        R(f"Framed({rname}, Tokenize, {lname})", lambda rnd=rnd, back=back: FramedCodecStack(rnd(), TokenizeCodec(), back()))
json.dump(log, open("log_r12_01.json", "w"), indent=1)
print("DONE r12")
