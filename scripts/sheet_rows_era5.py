"""Write paste-ready rows for the ERA5-Pressure and ERA5-Single tabs of the leaderboard sheet.

Columns match the sheet exactly:

    Author | Compression | Variable | Default/all timestep(s) | Config Short |
    Version of compression-recommendations | Configuration |
    [opt] Throughput Compression [GB/s] | [opt] Throughput Decompression [GB/s]

`Configuration` is written the way the notebooks print it, `print(codec.get_config())`.
Throughput comes from `results/era5_throughput.csv` (see `scripts/throughput_era5.py`)
and is left empty for any variable that has not been measured.

    uv run python scripts/sheet_rows_era5.py
"""

import csv
import json
from pathlib import Path

import numcodecs.registry

import hackathon  # noqa: F401, registers codecs

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "@Lagnajee"
RECOMMENDATIONS_VERSION = "0.1.0a1"
HEADER = [
    "Author",
    "Compression",
    "Variable",
    "Default/all timestep(s)",
    "Config Short",
    "Version of compression-recommendations",
    "Configuration",
    "[opt] Throughput Compression [GB/s], measured relative to the original size",
    "[opt] Throughput Decompression [GB/s], measured relative to the original size",
]


def config_short(label: str) -> str:
    """Turn a sweep label such as 'meanabs 0.01 SPERR q p=98.7' into a readable summary."""
    parts = []
    if label.startswith("Safeguarded(Zero)"):
        parts.append("Recommended Safeguards")
    elif "safeguarded" in label.lower() or label.startswith("Safeguarded("):
        parts.append("Recommended Safeguards")
    if "PwRatio" in label or "PWRatio" in label or "relq" in label:
        parts.append("PwRatio")
    if "SPERR" in label or "Sperr" in label:
        parts.append("SPERR")
    if "SZ3" in label or "Sz3" in label:
        parts.append("SZ3")
    if "grid" in label or "absq" in label or "FSO" in label:
        parts.append("FixedScaleOffset grid")
    if "lossless" in label.lower():
        parts.append("Lossless" + (" Tokenize" if "Tokenize" in label else ""))
    if "meanabs" in label or "meanrel" in label:
        parts.append("(mean-bound tuned)")
    parts.append("LZMA")
    return " + ".join(dict.fromkeys(parts)).replace(" + (mean-bound tuned)", " (mean-bound tuned)")


def main() -> None:
    expected = json.loads((ROOT / "results" / "era5_expected.json").read_text())
    throughput = {}
    tp_path = ROOT / "results" / "era5_throughput.csv"
    if tp_path.exists():
        lines = [line for line in tp_path.read_text().splitlines() if not line.startswith("#")]
        throughput = {r["key"]: r for r in csv.DictReader(lines)}

    out_dir = ROOT / "leaderboard" / "sheet"
    out_dir.mkdir(parents=True, exist_ok=True)
    for leveltype, tab in (("pressure", "ERA5-Pressure"), ("single", "ERA5-Single")):
        labels = {r["variable"]: r["codec"] for r in csv.DictReader(open(ROOT / "results" / f"era5_{leveltype}.csv"))}
        keys = sorted(k for k in expected if k.startswith(f"{leveltype}/"))
        missing_tp = 0
        with open(out_dir / f"{tab}.tsv", "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(HEADER)
            for key in keys:
                var = key.split("/", 1)[1]
                config = json.loads((ROOT / "configs" / "era5" / leveltype / f"{var}.json").read_text())
                codec = numcodecs.registry.get_codec(config)
                tp = throughput.get(key)
                missing_tp += tp is None
                writer.writerow([
                    AUTHOR,
                    f"{expected[key]:.2f}",
                    var,
                    "default",
                    config_short(labels.get(var, "")),
                    RECOMMENDATIONS_VERSION,
                    str(codec.get_config()),
                    f"{float(tp['compression_gb_per_s']):.4f}" if tp else "",
                    f"{float(tp['decompression_gb_per_s']):.4f}" if tp else "",
                ])
        print(f"{tab}: {len(keys)} rows ({missing_tp} without throughput)")


if __name__ == "__main__":
    main()
