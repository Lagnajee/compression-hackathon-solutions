# Absolute Error Bound over Spatial Gradient (`04-challenges/03-spatial-gradient.ipynb`)

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/49
(entries are collected in the Google Sheet linked from that issue)

## Sheet row

| Field | Value |
|---|---|
| Challenge | 03-spatial-gradient |
| All Data | TRUE |
| Compression Ratio | 83.876 |
| Author | @Lagnajee |
| Version | compression-safeguards 1.0.0rc3 / numcodecs 0.15.1 |

## Codec configuration

```json
{"id": "combinators.stack", "codecs": [{"id": "safeguards", "codec": {"id": "sperr.rs", "mode": "q", "q": 0.000425, "_version": "0.2.0"}, "safeguards": [{"kind": "qoi_eb_stencil", "qoi": "(X[I[0]-5] - X[I[0]+5]) / 357.5", "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}], "type": "abs", "eb": 1e-06, "qoi_dtype": "lossless", "early_bound": {}}], "fixed_constants": {}, "lossless": {"for_codec": null, "for_corrections": {"id": "combinators.best", "codecs": [{"id": "combinators.stack", "codecs": [{"id": "tokenize"}, {"id": "bitmap-index", "max_bitmaps": 1, "cost_factor": 1}, {"id": "shuffle.typed-byte"}, {"id": "combinators.framed", "codecs": [{"id": "zstd", "level": 3, "checksum": false}]}]}, {"id": "combinators.stack", "codecs": [{"id": "delta.binary"}, {"id": "tokenize"}, {"id": "bitmap-index", "max_bitmaps": 1, "cost_factor": 1}, {"id": "shuffle.typed-byte"}, {"id": "combinators.framed", "codecs": [{"id": "zstd", "level": 3, "checksum": false}]}]}]}}, "compute": {"unstable_iterative": false, "unstable_lossless_corrections": false}, "_version": "1.0.0"}, {"id": "lzma", "format": 1, "check": -1, "preset": 2147483657, "filters": null}]}
```
