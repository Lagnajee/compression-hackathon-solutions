# ERA5 pressure-level variables

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/56
(entries are collected in the Google Sheet linked from that issue; one row per variable)

Each row passes `check_safety_requirements` for the one-timestep test subset used by the notebook
(`All Data` = FALSE). Full codec configs are in
[`configs/era5/pressure/`](../configs/era5/pressure/).

| Variable | All Data | Compression Ratio | Baseline `Safeguarded(Zero)` | Codec | Config |
|---|---|---|---|---|---|
| cc | FALSE | 48.897 | 48.886 | Safeguarded(Zero)+LZMA | [json](../configs/era5/pressure/cc.json) |
| ciwc | FALSE | 65.404 | 59.657 | PWRatio(FSO log2 i2 r=1.01)+LZMA d2 lc3 | [json](../configs/era5/pressure/ciwc.json) |
| clwc | FALSE | 46.921 | 46.14 | PWRatio(FSO log2 i2 r=1.01)+LZMA d2 lc3 | [json](../configs/era5/pressure/clwc.json) |
| crwc | FALSE | 58.604 | 58.549 | Safeguarded(Zero)+LZMA | [json](../configs/era5/pressure/crwc.json) |
| cswc | FALSE | 62.739 | 56.034 | PWRatio(FSO log2 i2 r=1.01)+LZMA | [json](../configs/era5/pressure/cswc.json) |
| d | FALSE | 13.509 | 11.133 | PWRatio(FSO log2 i2 r=1.05)+LZMA d2 lc0 | [json](../configs/era5/pressure/d.json) |
| o3 | FALSE | 86.581 | 43.45 | PWRatio(Sperr pwe r=1.01)+LZMA | [json](../configs/era5/pressure/o3.json) |
| pv | FALSE | 52.753 | 46.184 | Safeguarded(Sperr q 3.0*1e-07)+LZMA | [json](../configs/era5/pressure/pv.json) |
| q | FALSE | 38.615 | 25.933 | PWRatio(Sperr pwe r=1.01)+LZMA | [json](../configs/era5/pressure/q.json) |
| r | FALSE | 35.971 | 21.46 | PWRatio(Sperr pwe r=1.01)+LZMA | [json](../configs/era5/pressure/r.json) |
| t | FALSE | 787.739 | 222.131 | PWRatio(Sperr pwe r=1.01)+LZMA | [json](../configs/era5/pressure/t.json) |
| u | FALSE | 131.894 | 50.049 | Safeguarded(Sperr pwe 1.5*0.5)+LZMA | [json](../configs/era5/pressure/u.json) |
| v | FALSE | 135.898 | 46.149 | Safeguarded(Sperr pwe 1.5*0.5)+LZMA | [json](../configs/era5/pressure/v.json) |
| vo | FALSE | 16.138 | 13.291 | PWRatio(FSO log2 i2 r=1.05)+LZMA d2 lc3 | [json](../configs/era5/pressure/vo.json) |
| w | FALSE | 34.770 | 20.573 | Sperr pwe 0.01+LZMA | [json](../configs/era5/pressure/w.json) |
| z | FALSE | 132.182 | 31.134 | Sperr pwe 10.0+LZMA | [json](../configs/era5/pressure/z.json) |
