"""Record how faithful each ERA5 reconstruction is, next to its compression ratio.

The published safety requirements accept a codec whose error stays inside a
loose mean-error bound, even when that flattens the field. This script decodes
every exported codec and records the error relative to the field's own spread
(`rmse_over_std`) plus the number of distinct values that survive, so a
degenerate entry is visible rather than hidden behind a large ratio.

    uv run python scripts/fidelity_era5.py [workers]
"""

import csv
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def measure(key: str) -> dict:
    import numcodecs.registry
    import numpy as np

    import hackathon  # noqa: F401
    from hackathon import era5

    leveltype, var = key.split("/")
    codec = numcodecs.registry.get_codec(json.loads((ROOT / "configs" / "era5" / leveltype / f"{var}.json").read_text()))
    x = era5.field(leveltype, var)
    y = np.asarray(codec.decode(codec.encode(x))).reshape(x.shape)
    fin = np.isfinite(x)
    xs, ys = x[fin], y[fin]
    std = float(np.std(xs))
    rmse = float(np.sqrt(np.mean((ys - xs) ** 2)))
    return dict(key=key, rmse=round(rmse, 8), std=round(std, 8),
                rmse_over_std=round(rmse / std if std > 0 else 0.0, 4),
                distinct_in=int(np.unique(xs).size), distinct_out=int(np.unique(ys).size))


def main() -> None:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    keys = sorted(json.loads((ROOT / "results" / "era5_expected.json").read_text()))
    with Pool(workers) as pool:
        rows = sorted(pool.map(measure, keys), key=lambda r: r["key"])
    out = ROOT / "results" / "era5_fidelity.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    worst = sorted(rows, key=lambda r: -r["rmse_over_std"])[:5]
    print(f"wrote {out}")
    print("worst fidelity:", [(r["key"], r["rmse_over_std"], r["distinct_out"]) for r in worst])


if __name__ == "__main__":
    main()
