"""Build the best codec for each challenge, score it, and write its artefacts.

Writes `configs/<challenge>.json`, `leaderboard/<challenge>.md`, and
`results/expected.json`.

    uv run python solve.py                 # all challenges
    uv run python solve.py 02-relative-error-bound
"""

import json
import sys
from pathlib import Path

import hackathon  # noqa: F401, registers codecs
from hackathon.challenges import CHALLENGES, ROOT
from hackathon.codecs import BEST

LEADERBOARD = """\
# {name} (`04-challenges/{key}.ipynb`)

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/{issue}
(entries are collected in the Google Sheet linked from that issue)

## Sheet row

| Field | Value |
|---|---|
| Challenge | {key} |
| All Data | TRUE |
| Compression Ratio | {cr:.3f} |
| Author | @Lagnajee |
| Version | compression-safeguards 1.0.0rc3 / numcodecs 0.15.1 |

## Codec configuration

```json
{config}
```
"""


def main(keys: list[str]) -> int:
    expected_path = ROOT / "results" / "expected.json"
    expected = json.loads(expected_path.read_text()) if expected_path.exists() else {}
    failed = False

    for key in keys:
        challenge = CHALLENGES[key]
        codec = BEST[key]()
        result = challenge.evaluate(codec, challenge.load())
        status = "OK" if result.ok else "VIOLATIONS"
        print(f"{key}: CR={result.compression_ratio:.4f} violations={result.violations} [{status}]")
        if not result.ok:
            failed = True
            continue

        config = codec.get_config()
        (ROOT / "configs" / f"{key}.json").write_text(json.dumps(config, indent=2) + "\n")
        (ROOT / "leaderboard" / f"{key}.md").write_text(
            LEADERBOARD.format(name=challenge.name, key=key, issue=challenge.leaderboard_issue, cr=result.compression_ratio, config=json.dumps(config))
        )
        expected[key] = round(result.compression_ratio, 4)

    expected_path.write_text(json.dumps(expected, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or list(CHALLENGES)))
