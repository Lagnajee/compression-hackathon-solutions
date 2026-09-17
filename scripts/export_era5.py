"""Turn ERA5 sweep logs into repository artefacts.

Inputs are the sweep outputs from `exploration/`:
- 04 pressure-level: one JSON list of rows (`log04.json`)
- 05 single-level: a directory with one JSON list per variable (`results05/`)

Each row has `var`, `codec`, `cr`, `ok` and `config`. For every variable the
best passing row is exported to:
- `configs/era5/<leveltype>/<var>.json`
- `results/era5_expected.json` (read by `verify_era5.py`)
- `results/era5_<leveltype>.csv` (best vs the `Safeguarded(Zero)` baseline)
- `leaderboard/era5-<leveltype>.md` (rows for the Google Sheet)

    uv run python scripts/export_era5.py --pressure path/log04.json path/log04b.json --single path/results05
"""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "Safeguarded(Zero)"
ISSUE = {"pressure": 56, "single": 57}
AUTHOR = "@Lagnajee"


def rows_from(path: Path) -> list[dict]:
    if path.is_dir():
        return [row for f in sorted(path.glob("*.json")) for row in json.loads(f.read_text())]
    return json.loads(path.read_text())


def export(leveltype: str, rows: list[dict], expected: dict) -> list[dict]:
    by_var: dict[str, dict] = {}
    for row in rows:
        if "var" not in row or "codec" not in row:
            continue
        entry = by_var.setdefault(row["var"], {"best": None, "baseline": None, "requirements": None})
        if row["codec"] == BASELINE and row.get("ok"):
            entry["baseline"] = row["cr"]
        if row.get("ok") and (entry["best"] is None or row["cr"] > entry["best"]["cr"]):
            entry["best"] = row
    for row in rows:  # 05 logs carry requirement strings in a header row
        if "requirements" in row and row.get("var") in by_var:
            by_var[row["var"]]["requirements"] = "; ".join(row["requirements"])
    for var, entry in by_var.items():  # 04 logs do not, so look them up
        if entry["requirements"] is None:
            try:
                from hackathon import era5

                entry["requirements"] = "; ".join(r.humanise() for r in era5.requirements(leveltype, var))
            except Exception:  # noqa: BLE001
                entry["requirements"] = ""

    # Fidelity overrides: some requirements are loose enough that the
    # highest-ratio passing codec flattens the field. exploration/era5/
    # pick_fidelity.py re-picks those, and its choice wins here.
    fidelity_path = ROOT / "exploration" / "era5" / "fidelity_choice.json"
    if leveltype == "single" and fidelity_path.exists():
        for choice in json.loads(fidelity_path.read_text()):
            entry = by_var.get(choice["var"])
            if entry is not None and choice.get("cr"):
                entry["best"] = {"cr": choice["cr"], "codec": choice["codec"], "config": choice["config"], "ok": True}

    config_dir = ROOT / "configs" / "era5" / leveltype
    config_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for var in sorted(by_var):
        entry = by_var[var]
        best = entry["best"]
        if best is None:
            summary.append(dict(variable=var, best_cr="", codec="NO PASSING CODEC", baseline_cr=entry["baseline"] or "", gain="", requirements=entry["requirements"] or ""))
            continue
        (config_dir / f"{var}.json").write_text(json.dumps(best["config"], indent=2) + "\n")
        expected[f"{leveltype}/{var}"] = round(best["cr"], 4)
        gain = round(best["cr"] / entry["baseline"], 2) if entry["baseline"] else ""
        summary.append(dict(variable=var, best_cr=best["cr"], codec=best["codec"], baseline_cr=entry["baseline"] or "", gain=gain, requirements=entry["requirements"] or ""))

    with (ROOT / "results" / f"era5_{leveltype}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]) if summary else ["variable"])
        writer.writeheader()
        writer.writerows(summary)

    lines = [
        f"# ERA5 {leveltype}-level variables",
        "",
        f"Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/{ISSUE[leveltype]}",
        "(entries are collected in the Google Sheet linked from that issue; one row per variable)",
        "",
        "Each row passes `check_safety_requirements` for the one-timestep test subset used by the notebook",
        "(`All Data` = FALSE). Full codec configs are in",
        f"[`configs/era5/{leveltype}/`](../configs/era5/{leveltype}/).",
        "",
        "| Variable | All Data | Compression Ratio | Author | Baseline `Safeguarded(Zero)` | Codec | Config |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in summary:
        if s["best_cr"] == "":
            lines.append(f"| {s['variable']} | FALSE | — | {AUTHOR} | {s['baseline_cr']} | no passing codec | — |")
        else:
            lines.append(
                f"| {s['variable']} | FALSE | {s['best_cr']:.3f} | {AUTHOR} | {s['baseline_cr']} | {s['codec']} | "
                f"[json](../configs/era5/{leveltype}/{s['variable']}.json) |"
            )
    (ROOT / "leaderboard" / f"era5-{leveltype}.md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pressure", type=Path, nargs="+", help="one or more logs; the best passing row per variable wins")
    parser.add_argument("--single", type=Path, nargs="+", help="one or more logs or per-variable log directories")
    args = parser.parse_args()

    expected_path = ROOT / "results" / "era5_expected.json"
    expected = json.loads(expected_path.read_text()) if expected_path.exists() else {}
    for leveltype, paths in (("pressure", args.pressure), ("single", args.single)):
        if not paths:
            continue
        summary = export(leveltype, [row for path in paths for row in rows_from(path)], expected)
        passed = [s for s in summary if s["best_cr"] != ""]
        print(f"{leveltype}: {len(passed)}/{len(summary)} variables exported")
    expected_path.write_text(json.dumps(dict(sorted(expected.items())), indent=2) + "\n")


if __name__ == "__main__":
    main()
