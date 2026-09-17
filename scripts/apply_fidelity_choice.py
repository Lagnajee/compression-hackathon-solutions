"""Apply the fidelity-filtered codec choices from exploration/era5/pick_fidelity.py.

Rewrites `configs/era5/single/<var>.json`, `results/era5_expected.json` and the
affected rows of `results/era5_single.csv` for variables whose previous codec
passed the official checks only by flattening the field.

    uv run python scripts/apply_fidelity_choice.py
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    choices = [c for c in json.loads((ROOT / "exploration" / "era5" / "fidelity_choice.json").read_text()) if c.get("cr")]
    expected_path = ROOT / "results" / "era5_expected.json"
    expected = json.loads(expected_path.read_text())
    csv_path = ROOT / "results" / "era5_single.csv"
    rows = list(csv.DictReader(open(csv_path)))
    by_var = {r["variable"]: r for r in rows}

    for c in choices:
        var = c["var"]
        (ROOT / "configs" / "era5" / "single" / f"{var}.json").write_text(json.dumps(c["config"], indent=2) + "\n")
        expected[f"single/{var}"] = round(c["cr"], 4)
        row = by_var[var]
        row["best_cr"] = c["cr"]
        row["codec"] = c["codec"]
        row["gain"] = round(c["cr"] / float(row["baseline_cr"]), 2) if row["baseline_cr"] else ""
        print(f"{var}: -> x{c['cr']:.2f}  {c['codec']}  (err/std {c['nrmse']}, {c['uniq']} distinct)")

    expected_path.write_text(json.dumps(dict(sorted(expected.items())), indent=2) + "\n")
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"applied {len(choices)} fidelity-filtered choices")


if __name__ == "__main__":
    main()
