"""Rebuild every ERA5 codec from `configs/era5/<leveltype>/<var>.json` and re-check it.

Fails if any variable no longer satisfies its safety requirements or its
compression ratio drifts from `results/era5_expected.json` by more than 0.1%.

    uv run python verify_era5.py                  # all stored variables
    uv run python verify_era5.py pressure/u single/2t
    uv run python verify_era5.py --sample 6       # every n-th variable, for CI
"""

import json
import sys

import numcodecs.registry

import hackathon  # noqa: F401, registers codecs
from hackathon import era5
from hackathon.challenges import ROOT

TOLERANCE = 1e-3


def main(selected: list[str]) -> int:
    expected = json.loads((ROOT / "results" / "era5_expected.json").read_text())
    keys = sorted(expected)
    if selected[:1] == ["--sample"]:
        n = int(selected[1])
        keys = keys[:: max(1, len(keys) // n)][:n]
    elif selected:
        keys = selected
    failed = False

    for key in keys:
        leveltype, var = key.split("/")
        config = json.loads((ROOT / "configs" / "era5" / leveltype / f"{var}.json").read_text())
        codec = numcodecs.registry.get_codec(config)
        result = era5.evaluate(codec, leveltype, var)

        drift = abs(result.compression_ratio - expected[key]) / expected[key]
        ok = result.ok and drift <= TOLERANCE
        failed |= not ok
        print(
            f"{'PASS' if ok else 'FAIL'} {key}: CR={result.compression_ratio:.4f} "
            f"(expected {expected[key]}) requirements={'met' if result.ok else 'VIOLATED'}"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
