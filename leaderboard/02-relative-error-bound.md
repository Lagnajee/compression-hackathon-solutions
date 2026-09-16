# Pointwise Relative Error Bound (`04-challenges/02-relative-error-bound.ipynb`)

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/48
(entries are collected in the Google Sheet linked from that issue)

## Sheet row

| Field | Value |
|---|---|
| Challenge | 02-relative-error-bound |
| All Data | TRUE |
| Compression Ratio | 19.071 |
| Author | @Lagnajee |
| Version | compression-safeguards 1.0.0rc3 / numcodecs 0.15.1 |

## Codec configuration

```json
{"id": "combinators.stack", "codecs": [{"id": "pw_ratio", "eb_ratio": 1.01, "eb_abs_marker": "$eb_abs", "log_codec": {"id": "combinators.stack", "codecs": [{"id": "fixedscaleoffset", "scale": 34.83384183097051, "offset": 0, "dtype": "<f8", "astype": "<i2"}, {"id": "bitmap-index", "max_bitmaps": 1, "cost_factor": 1}]}, "sign_codec": {"id": "zstd.rs", "level": 19, "_version": "0.1.0"}}, {"id": "lzma", "format": 3, "check": -1, "preset": null, "filters": [{"id": 3, "dist": 2}, {"id": 33, "preset": 2147483657, "lc": 1, "lp": 1, "pb": 1}]}]}
```
