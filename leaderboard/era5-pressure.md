# ERA5 pressure-level variables

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/56
(entries are collected in the Google Sheet linked from that issue; one row per variable)

Each row passes `check_safety_requirements` for the one-timestep test subset used by the notebook
(`All Data` = FALSE). Full codec configs are in
[`configs/era5/pressure/`](../configs/era5/pressure/).

| Variable | All Data | Compression Ratio | Baseline `Safeguarded(Zero)` | Codec | Config |
|---|---|---|---|---|---|
| cc | FALSE | 48.886 | 48.886 | Safeguarded(Zero) | [json](../configs/era5/pressure/cc.json) |
| ciwc | FALSE | 65.385 | 59.657 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/ciwc.json) |
| clwc | FALSE | 46.902 | 46.14 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/clwc.json) |
| crwc | FALSE | 58.549 | 58.549 | Safeguarded(Zero) | [json](../configs/era5/pressure/crwc.json) |
| cswc | FALSE | 62.739 | 56.034 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/cswc.json) |
| d | FALSE | 13.506 | 11.133 | PWRatio(FSO log2 i2 r=1.05)+LZMA | [json](../configs/era5/pressure/d.json) |
| o3 | FALSE | 58.002 | 43.45 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/o3.json) |
| pv | FALSE | 47.139 | 46.184 | Sperr pwe 1e-07 | [json](../configs/era5/pressure/pv.json) |
| q | FALSE | 33.385 | 25.933 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/q.json) |
| r | FALSE | 28.417 | 21.46 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/r.json) |
| t | FALSE | 331.786 | 222.131 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/t.json) |
| u | FALSE | 118.513 | 50.049 | Sperr pwe 0.5 | [json](../configs/era5/pressure/u.json) |
| v | FALSE | 121.272 | 46.149 | Sperr pwe 0.5 | [json](../configs/era5/pressure/v.json) |
| vo | FALSE | 16.132 | 13.291 | PWRatio(FSO log2 i2 r=1.05)+LZMA | [json](../configs/era5/pressure/vo.json) |
| w | FALSE | 34.555 | 20.573 | Sperr pwe 0.01 | [json](../configs/era5/pressure/w.json) |
| z | FALSE | 126.688 | 31.134 | Sperr pwe 10.0 | [json](../configs/era5/pressure/z.json) |
