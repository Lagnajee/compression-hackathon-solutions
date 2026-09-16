"""Write paste-ready rows for the NaN, PwRel and Gradient tabs of the leaderboard sheet.

Columns match those tabs exactly:

    Author | Compression | Config Short | Configuration |
    [opt] Throughput Compression [GB/s] | [opt] Throughput Decompression [GB/s]

`Configuration` is written the way the notebooks print it, `print(codec.get_config())`.
Ratios come from `results/expected.json` (written by `solve.py`) and throughput
from `results/challenges_throughput.csv` (see `scripts/throughput_challenges.py`),
left empty when a challenge has not been measured.

    uv run python scripts/sheet_rows_challenges.py
"""

import csv
import json
from pathlib import Path

import numcodecs.registry

import hackathon  # noqa: F401, registers codecs

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "@Lagnajee"
TABS = {
    "01-nan-missing-values": ("NaN", "Round + Tokenize + BitmapIndex + LZMA"),
    "02-relative-error-bound": ("PwRel", "PwRatio + FixedScaleOffset log grid + BitmapIndex + LZMA"),
    "03-spatial-gradient": ("Gradient", "Safeguards (stencil QoI) + SPERR + LZMA"),
}


def main() -> None:
    expected = json.loads((ROOT / "results" / "expected.json").read_text())
    tp_path = ROOT / "results" / "challenges_throughput.csv"
    throughput = {}
    if tp_path.exists():
        lines = [line for line in tp_path.read_text().splitlines() if not line.startswith("#")]
        throughput = {r["challenge"]: r for r in csv.DictReader(lines)}
    out_dir = ROOT / "leaderboard" / "sheet"
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, (tab, short) in TABS.items():
        config = json.loads((ROOT / "configs" / f"{key}.json").read_text())
        codec = numcodecs.registry.get_codec(config)
        with open(out_dir / f"{tab}.tsv", "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([
                "Author", "Compression", "Config Short", "Configuration",
                "[opt] Throughput Compression [GB/s], measured relative to the original size",
                "[opt] Throughput Decompression [GB/s], measured relative to the original size",
            ])
            tp = throughput.get(key)
            writer.writerow([
                AUTHOR, f"{expected[key]:.2f}", short, str(codec.get_config()),
                f"{float(tp['compression_gb_per_s']):.4f}" if tp else "",
                f"{float(tp['decompression_gb_per_s']):.4f}" if tp else "",
            ])
        print(f"{tab}: x{expected[key]:.2f}  {short}")


if __name__ == "__main__":
    main()
