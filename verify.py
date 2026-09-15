"""Rebuild every codec from `configs/*.json` alone and check it still passes.

Fails if any challenge has violations or its compression ratio drifts from
`results/expected.json` by more than 0.1%.

    uv run python verify.py
"""

import json
import sys

import numcodecs.registry

import hackathon  # noqa: F401, registers codecs
from hackathon.challenges import CHALLENGES, ROOT

TOLERANCE = 1e-3


def main() -> int:
    expected = json.loads((ROOT / "results" / "expected.json").read_text())
    failed = False

    for key, challenge in CHALLENGES.items():
        config = json.loads((ROOT / "configs" / f"{key}.json").read_text())
        codec = numcodecs.registry.get_codec(config)
        result = challenge.evaluate(codec, challenge.load())

        drift = abs(result.compression_ratio - expected[key]) / expected[key]
        ok = result.ok and drift <= TOLERANCE
        failed |= not ok
        print(
            f"{'PASS' if ok else 'FAIL'} {key}: CR={result.compression_ratio:.4f} "
            f"(expected {expected[key]}) violations={result.violations} time={result.seconds:.1f}s"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
