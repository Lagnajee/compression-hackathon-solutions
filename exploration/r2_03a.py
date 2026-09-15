import json, numpy as np, harness as h
from numcodecs_wasm_sz3 import Sz3
from numcodecs_wasm_sperr import Sperr
da = h.load_03(); log = []
R = lambda n, f: h.run("03", n, f, da, log)
for eb in [1.7875e-4, 2.0e-4, 2.3e-4, 2.6e-4, 2.9e-4, 3.2e-4]:
    R(f"Sperr pwe {eb}", lambda eb=eb: Sperr(mode="pwe", pwe=eb))
for p in ["interpolation","interpolation-lorenzo","regression","lorenzo2","lorenzo2-regression","lorenzo","lorenzo-regression","lorenzo-lorenzo2","lorenzo-lorenzo2-regression"]:
    R(f"Sz3 abs 1.7874e-4 {p}", lambda p=p: Sz3(eb_mode="abs", eb_abs=1.7874e-4, predictor=p))
json.dump(log, open("log_r2_03a.json", "w"), indent=1)
print("DONE r2_03a")
