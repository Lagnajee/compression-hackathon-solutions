# ERA5 single-level variables

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/57
(entries are collected in the Google Sheet linked from that issue; one row per variable)

Each row passes `check_safety_requirements` for the one-timestep test subset used by the notebook
(`All Data` = FALSE). Full codec configs are in
[`configs/era5/single/`](../configs/era5/single/).

| Variable | All Data | Compression Ratio | Baseline `Safeguarded(Zero)` | Codec | Config |
|---|---|---|---|---|---|
| 100u | FALSE | 12.564 | 8.404 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/100u.json) |
| 100v | FALSE | 14.281 | 8.167 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/100v.json) |
| wstar | FALSE | 33.782 | 20.713 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/wstar.json) |
| z | FALSE | 23.634 | 16.933 | absq pointwise 10 | [json](../configs/era5/single/z.json) |
