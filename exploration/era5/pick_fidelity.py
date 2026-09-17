"""Re-pick single-level codecs that keep the reconstruction meaningful.

The official checks accept a codec whose error stays inside a loose mean-error
bound, even when that means flattening the field to (nearly) a constant. This
script re-picks, for the affected variables, the highest-ratio logged candidate
that also passes a fidelity test:

    RMSE <= FIDELITY_NRMSE * std(original)   and   > MIN_UNIQUE distinct values

A coarse quantiser that keeps only a handful of levels is fine as long as its
error is small relative to the field; the distinct-value guard only catches
reconstructions that collapse to a (near) constant.

Writes exploration/era5/fidelity_choice.json.

    uv run python exploration/era5/pick_fidelity.py [workers]
"""

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numcodecs.registry
import numpy as np

import hackathon  # noqa: F401
from hackathon import era5

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIDELITY_NRMSE = 0.3
MIN_UNIQUE = 3  # only guards against collapse to a (near) constant field


def fidelity(x, y):
    fin = np.isfinite(x)
    xs, ys = x[fin], y[fin]
    std = float(np.std(xs))
    rmse = float(np.sqrt(np.mean((ys - xs) ** 2)))
    return (rmse / std if std > 0 else 0.0), int(np.unique(ys).size)


def candidates_for(var):
    rows = []
    for d in ("results05", "results05_ext", "search_single"):
        p = HERE / d / f"{var}.json"
        if p.exists():
            rows += [r for r in json.loads(p.read_text()) if r.get("ok") and r.get("config")]
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: -r["cr"]):
        k = json.dumps(r["config"], sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def refit(var):
    x = era5.field("single", var)
    for r in candidates_for(var):
        try:
            codec = numcodecs.registry.get_codec(json.loads(json.dumps(r["config"])))
            y = np.asarray(codec.decode(codec.encode(x))).reshape(x.shape)
        except Exception:  # noqa: BLE001
            continue
        nrmse, uniq = fidelity(x, y)
        if nrmse <= FIDELITY_NRMSE and uniq >= MIN_UNIQUE:
            print(f"{var}: {r['cr']} {r.get('codec', '?')} (err/std {nrmse:.2f}, {uniq} distinct)", flush=True)
            return dict(var=var, cr=r["cr"], codec=r.get("codec"), nrmse=round(nrmse, 4), uniq=uniq, config=r["config"])
    print(f"{var}: NO fidelity-passing candidate", flush=True)
    return dict(var=var, cr=None)


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    flagged = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
    if flagged is None:
        fid = json.loads(Path("/tmp/claude-1000/-home-lagnajeet-Desktop-sarab-training-unet-Res-UNET/248afae3-abc5-4f1d-9627-86e13a879fa7/scratchpad/fidelity_single.json").read_text())
        flagged = [r["var"] for r in fid if r["nrmse"] > FIDELITY_NRMSE or r["uniq_out"] <= MIN_UNIQUE]
    print(f"refitting {len(flagged)} variables with {workers} workers", flush=True)
    with Pool(workers) as pool:
        out = list(pool.imap_unordered(refit, flagged))
    (HERE / "fidelity_choice.json").write_text(json.dumps(out, indent=1, default=str))
    print("DONE")
