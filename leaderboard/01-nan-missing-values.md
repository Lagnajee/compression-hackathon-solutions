# Missing Values (`04-challenges/01-nan-missing-values.ipynb`)

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/47
(entries are collected in the Google Sheet linked from that issue)

## Sheet row

| Field | Value |
|---|---|
| Challenge | 01-nan-missing-values |
| All Data | TRUE |
| Compression Ratio | 42.802 |
| Author | @Lagnajee |
| Version | compression-safeguards 1.0.0rc3 / numcodecs 0.15.1 |

## Codec configuration

```json
{"id": "combinators.framed", "codecs": [{"id": "round.rs", "precision": 2.0, "_version": "1.0.0"}, {"id": "tokenize"}, {"id": "lzma", "format": 3, "check": -1, "preset": null, "filters": [{"id": 33, "preset": 2147483657, "lc": 4, "lp": 0, "pb": 0}]}]}
```
