import json, lzma, contextlib, io, numpy as np, harness as h
from numcodecs import LZMA, AsType
from numcodecs_combinators.stack import CodecStack
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_wasm_zstd import Zstd
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_ebcc import Ebcc
from numcodecs_wasm_lc import Lc
from numcodecs_wasm_bit_round import BitRound
from numcodecs_wasm_pressio import Pressio
da = h.load_02(); log = []
def R(n, f, quiet=False):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): row = h.run("02", n, f, da, log)
    if not quiet: print(row, flush=True)
def pw(cfg, key, ratio=1.01):
    return PointwiseRatioErrorBoundedCodec(eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec={**cfg, key: "$eb_abs"}, sign_codec=Zstd(level=19))
PRED = ["interpolation","interpolation-lorenzo","regression","lorenzo2","lorenzo2-regression","lorenzo","lorenzo-regression","lorenzo-lorenzo2","lorenzo-lorenzo2-regression"]
for p in PRED:
    R(f"PWRatio(Sz3 {p}) 1.01", lambda p=p: pw(Sz3(eb_mode="abs", eb_abs=1.0, predictor=p).get_config(), "eb_abs"))
    R(f"AsType f4 + PWRatio(Sz3 {p}) 1.0099", lambda p=p: CodecStack(AsType(encode_dtype="f4", decode_dtype="f8"), pw(Sz3(eb_mode="abs", eb_abs=1.0, predictor=p).get_config(), "eb_abs", 1.0099)))
R("PWRatio(Ebcc abs) 1.01", lambda: pw(Ebcc(base_cr=100, residual="absolute", error=1.0).get_config(), "error"))
R("AsType f4 + PWRatio(Ebcc abs) 1.0099", lambda: CodecStack(AsType(encode_dtype="f4", decode_dtype="f8"), pw(Ebcc(base_cr=100, residual="absolute", error=1.0).get_config(), "error", 1.0099)))
R("BitRound rel + lzma9e", lambda: CodecStack(BitRound(mode="rel", eb_rel=0.01), LZMA(preset=9 | lzma.PRESET_EXTREME)))
R("Pressio pw_rel linear_quantizer bzip2", lambda: Pressio(compressor_id="pw_rel", early_config={"pw_rel:abs_comp": "linear_quantizer", "linear_quantizer:compressor": "bzip2", "pw_rel:sign_comp": "bzip2"}, compressor_config={"pressio:pw_rel": 0.01}))
A = [("DIFFMS",8),("DIFFNB",8),("TCMS",8),("BIT",8)]
B = [(c,s) for c in ["RLE","RRE","RZE","RARE","RAZE","CLOG","HCLOG"] for s in (1,8)]
pipes = [[b] for b in B] + [[a,b] for a in A for b in B] + [[a1,a2,b] for a1 in A for a2 in A if a1!=a2 for b in B]
for p in pipes:
    comps = [{"id":c,"size":s} for c,s in p]
    R("LC REL0.01 " + " ".join(f"{c}{s}" for c,s in p), lambda comps=comps: Lc(preprocessors=[{"id":"QUANT","dtype":"f64","kind":"REL","error_bound":0.01,"decorrelation":"0"}], components=comps), quiet=True)
json.dump(log, open("log_r2_02.json", "w"), indent=1)
ok = sorted([r for r in log if r.get("ok")], key=lambda r: -r["cr"])
print("TOP02:"); [print(r) for r in ok[:15]]
print("ERRORS:", [r["name"] + " " + r["error"][:120] for r in log if "error" in r][:6])
print("DONE r2_02")
