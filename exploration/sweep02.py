import json, numpy as np, harness as h
from numcodecs_combinators.stack import CodecStack
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_zero import ZeroCodec
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_wasm_zstd import Zstd
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_zfp import Zfp
from numcodecs_wasm_sperr import Sperr
from numcodecs_wasm_lc import Lc
from numcodecs_wasm_bit_round import BitRound
da = h.load_02(); log = []
R = lambda n, f: h.run("02", n, f, da, log)
def pw(cfg, key, ratio=1.01):
    return PointwiseRatioErrorBoundedCodec(eb_ratio=ratio, eb_abs_marker="$eb_abs", log_codec={**cfg, key: "$eb_abs"}, sign_codec=Zstd(level=19))
R("Sz3 rel 0.01 (notebook default, range-rel)", lambda: Sz3(eb_mode="rel", eb_rel=0.01))
R("BitRound rel0.01 + Zstd19", lambda: CodecStack(BitRound(mode="rel", eb_rel=0.01), Zstd(level=19)))
R("Lc QUANT REL f64 0.01 BIT RLE", lambda: Lc(preprocessors=[{"id":"QUANT","dtype":"f64","kind":"REL","error_bound":0.01,"decorrelation":"0"}], components=[{"id":"BIT","size":8},{"id":"RLE","size":8}]))
for p in ["interpolation-lorenzo", "interpolation", "lorenzo"]:
    R(f"PWRatio(Sz3 abs {p}) 1.01", lambda p=p: pw(Sz3(eb_mode="abs", eb_abs=1.0, predictor=p).get_config(), "eb_abs"))
R("PWRatio(Zfp) 1.01", lambda: pw(Zfp(mode="fixed-accuracy", tolerance=1.0).get_config(), "tolerance"))
R("PWRatio(Sperr pwe) 1.01", lambda: pw(Sperr(mode="pwe", pwe=1.0).get_config(), "pwe"))
R("Safeguarded(Zero) rel0.01", lambda: SafeguardedCodec(codec=ZeroCodec(), safeguards=[{"kind":"eb","type":"rel","eb":0.01}]))
R("Safeguarded(PWRatio Sz3 1.01) rel0.01", lambda: SafeguardedCodec(codec=pw(Sz3(eb_mode="abs", eb_abs=1.0).get_config(), "eb_abs"), safeguards=[{"kind":"eb","type":"rel","eb":0.01}]))
for r in [1.02, 1.05]:
    R(f"Safeguarded(PWRatio Sz3 {r}) rel0.01", lambda r=r: SafeguardedCodec(codec=pw(Sz3(eb_mode="abs", eb_abs=1.0).get_config(), "eb_abs", r), safeguards=[{"kind":"eb","type":"rel","eb":0.01}]))
json.dump(log, open("log02.json", "w"), indent=1)
print("DONE02")
