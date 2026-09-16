# ERA5 single-level variables

Leaderboard: https://github.com/climet-eu/compression-lab-notebooks/issues/57
(entries are collected in the Google Sheet linked from that issue; one row per variable)

Each row passes `check_safety_requirements` for the one-timestep test subset used by the notebook
(`All Data` = FALSE). Full codec configs are in
[`configs/era5/single/`](../configs/era5/single/).

| Variable | All Data | Compression Ratio | Author | Baseline `Safeguarded(Zero)` | Codec | Config |
|---|---|---|---|---|---|---|
| 100u | FALSE | 19.289 | @Lagnajee | 8.404 | meanabs 0.01 SPERR q p=4.362 | [json](../configs/era5/single/100u.json) |
| 100v | FALSE | 19.469 | @Lagnajee | 8.167 | meanabs 0.01 SPERR q p=4.362 | [json](../configs/era5/single/100v.json) |
| 10fg | FALSE | 76.190 | @Lagnajee | 45.545 | meanabs 0.5 SZ3 abs p=1 | [json](../configs/era5/single/10fg.json) |
| 10u | FALSE | 11798.182 | @Lagnajee | 42.526 | meanabs 0.5 SPERR q p=362 | [json](../configs/era5/single/10u.json) |
| 10v | FALSE | 11536.000 | @Lagnajee | 41.287 | meanrel 0.5 (abs) SPERR pwe p=53.82 | [json](../configs/era5/single/10v.json) |
| 2d | FALSE | 23.436 | @Lagnajee | 16.497 | pwabs 0.05 safeguarded SZ3 abs p=1 | [json](../configs/era5/single/2d.json) |
| 2t | FALSE | 24.960 | @Lagnajee | 17.471 | pwabs 0.05 safeguarded SZ3 abs p=1 | [json](../configs/era5/single/2t.json) |
| alnid | FALSE | 1773.254 | @Lagnajee | 86.423 | meanabs 0.01 SPERR q p=34.9 | [json](../configs/era5/single/alnid.json) |
| alnip | FALSE | 2264.427 | @Lagnajee | 90.739 | meanabs 0.01 SPERR q p=38.05 | [json](../configs/era5/single/alnip.json) |
| aluvd | FALSE | 10815.000 | @Lagnajee | 142.826 | meanabs 0.01 SPERR q p=98.7 | [json](../configs/era5/single/aluvd.json) |
| aluvp | FALSE | 11163.871 | @Lagnajee | 143.22 | meanabs 0.01 SPERR q p=98.7 | [json](../configs/era5/single/aluvp.json) |
| anor | FALSE | 191.257 | @Lagnajee | 44.269 | meanabs 0.1 SPERR q p=13.45 | [json](../configs/era5/single/anor.json) |
| asn | FALSE | 1677.286 | @Lagnajee | 578.568 | meanrel 0.001 (abs) SPERR q p=83 | [json](../configs/era5/single/asn.json) |
| avg_cpr | FALSE | 31.259 | @Lagnajee | 18.149 | meanrel 0.01 (abs) grid p=5.187 | [json](../configs/era5/single/avg_cpr.json) |
| avg_csfr | FALSE | 398.671 | @Lagnajee | 226.628 | meanrel 0.01 (abs) grid p=76.11 | [json](../configs/era5/single/avg_csfr.json) |
| avg_esrwe | FALSE | 33091.315 | @Lagnajee | 100.453 | absq meanabs 1e-07 eb=256.0v | [json](../configs/era5/single/avg_esrwe.json) |
| avg_ibld | FALSE | 120.418 | @Lagnajee | 22.564 | meanabs 0.1 SPERR q p=9.514 | [json](../configs/era5/single/avg_ibld.json) |
| avg_ie | FALSE | 36.187 | @Lagnajee | 11.78 | meanrel 0.01 (abs) SPERR q p=5.657 | [json](../configs/era5/single/avg_ie.json) |
| avg_iegwss | FALSE | 64.850 | @Lagnajee | 45.674 | meanrel 0.01 (abs) grid p=8.724 | [json](../configs/era5/single/avg_iegwss.json) |
| avg_iews | FALSE | 33.091 | @Lagnajee | 10.663 | meanrel 0.01 (abs) SPERR q p=5.657 | [json](../configs/era5/single/avg_iews.json) |
| avg_igwd | FALSE | 57.245 | @Lagnajee | 57.245 | Safeguarded(Zero) | [json](../configs/era5/single/avg_igwd.json) |
| avg_ilspf | FALSE | 26.918 | @Lagnajee | 14.518 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/avg_ilspf.json) |
| avg_ingwss | FALSE | 54.366 | @Lagnajee | 50.333 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/avg_ingwss.json) |
| avg_inss | FALSE | 32.586 | @Lagnajee | 10.564 | meanrel 0.01 (abs) SPERR q p=5.657 | [json](../configs/era5/single/avg_inss.json) |
| avg_ishf | FALSE | 16.764 | @Lagnajee | 8.116 | meanabs 0.1 SPERR q p=4.362 | [json](../configs/era5/single/avg_ishf.json) |
| avg_lsprate | FALSE | 32.583 | @Lagnajee | 18.681 | meanrel 0.01 (abs) grid p=3.364 | [json](../configs/era5/single/avg_lsprate.json) |
| avg_lssfr | FALSE | 153.359 | @Lagnajee | 57.256 | meanrel 0.01 (abs) grid p=10.37 | [json](../configs/era5/single/avg_lssfr.json) |
| avg_pevr | FALSE | 71.247 | @Lagnajee | 29.267 | absq meanrel 0.01 eb=8v*mean|x| | [json](../configs/era5/single/avg_pevr.json) |
| avg_rorwe | FALSE | 78.713 | @Lagnajee | 46.132 | meanrel 0.01 (abs) grid p=11.31 | [json](../configs/era5/single/avg_rorwe.json) |
| avg_sdirswrf | FALSE | 25.264 | @Lagnajee | 13.624 | absq meanabs 0.1 eb=4v | [json](../configs/era5/single/avg_sdirswrf.json) |
| avg_sdirswrfcs | FALSE | 61.900 | @Lagnajee | 22.86 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_sdirswrfcs.json) |
| avg_sdlwrf | FALSE | 20.470 | @Lagnajee | 10.292 | meanabs 0.1 SPERR q p=4.362 | [json](../configs/era5/single/avg_sdlwrf.json) |
| avg_sdlwrfcs | FALSE | 51.038 | @Lagnajee | 14.019 | meanabs 0.1 SPERR q p=6.169 | [json](../configs/era5/single/avg_sdlwrfcs.json) |
| avg_sdswrf | FALSE | 24.019 | @Lagnajee | 14.137 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_sdswrf.json) |
| avg_sdswrfcs | FALSE | 62.684 | @Lagnajee | 23.852 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_sdswrfcs.json) |
| avg_sduvrf | FALSE | 65.101 | @Lagnajee | 21.65 | absq meanabs 0.1 eb=5.6v | [json](../configs/era5/single/avg_sduvrf.json) |
| avg_slhtf | FALSE | 14.911 | @Lagnajee | 8.053 | meanabs 0.1 SPERR q p=4.362 | [json](../configs/era5/single/avg_slhtf.json) |
| avg_smr | FALSE | 21351.979 | @Lagnajee | 664.42 | absq meanabs 1e-06 eb=256.0v | [json](../configs/era5/single/avg_smr.json) |
| avg_snlwrf | FALSE | 17.966 | @Lagnajee | 8.872 | meanabs 0.1 SPERR q p=4.362 | [json](../configs/era5/single/avg_snlwrf.json) |
| avg_snlwrfcs | FALSE | 42.572 | @Lagnajee | 12.839 | meanabs 0.1 SPERR q p=5.657 | [json](../configs/era5/single/avg_snlwrfcs.json) |
| avg_snswrf | FALSE | 34.197 | @Lagnajee | 13.961 | meanabs 0.1 SPERR q p=8.724 | [json](../configs/era5/single/avg_snswrf.json) |
| avg_snswrfcs | FALSE | 44.497 | @Lagnajee | 19.739 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_snswrfcs.json) |
| avg_ssurfror | FALSE | 1986.112 | @Lagnajee | 49.435 | absq meanabs 1e-06 eb=45.0v | [json](../configs/era5/single/avg_ssurfror.json) |
| avg_surfror | FALSE | 7442.581 | @Lagnajee | 125.261 | absq meanabs 1e-06 eb=256.0v | [json](../configs/era5/single/avg_surfror.json) |
| avg_tdswrf | FALSE | 144.564 | @Lagnajee | 43.897 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_tdswrf.json) |
| avg_tnlwrf | FALSE | 24.320 | @Lagnajee | 10.545 | meanabs 0.1 SPERR q p=4.757 | [json](../configs/era5/single/avg_tnlwrf.json) |
| avg_tnlwrfcs | FALSE | 81.841 | @Lagnajee | 16.761 | meanabs 0.1 SPERR pwe p=5.187 | [json](../configs/era5/single/avg_tnlwrfcs.json) |
| avg_tnswrf | FALSE | 23.533 | @Lagnajee | 14.36 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_tnswrf.json) |
| avg_tnswrfcs | FALSE | 50.198 | @Lagnajee | 22.301 | meanabs 0.1 grid p=3.668 | [json](../configs/era5/single/avg_tnswrfcs.json) |
| avg_tprate | FALSE | 24.800 | @Lagnajee | 14.372 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/avg_tprate.json) |
| avg_tsrwe | FALSE | 126.734 | @Lagnajee | 55.499 | absq meanrel 0.01 eb=8v*mean|x| | [json](../configs/era5/single/avg_tsrwe.json) |
| avg_vimdf | FALSE | 13.282 | @Lagnajee | 8.272 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/avg_vimdf.json) |
| bfi | FALSE | 59.432 | @Lagnajee | 16.803 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/bfi.json) |
| bld | FALSE | 62.853 | @Lagnajee | 38.474 | absq meanabs 1000 eb=1.4v | [json](../configs/era5/single/bld.json) |
| blh | FALSE | 24.725 | @Lagnajee | 18.365 | absq meanabs 10 eb=1.0v | [json](../configs/era5/single/blh.json) |
| cape | FALSE | 32.424 | @Lagnajee | 14.108 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/cape.json) |
| cbh | FALSE | 10.798 | @Lagnajee | 9.047 | absq meanabs 1 eb=1.4v | [json](../configs/era5/single/cbh.json) |
| cdir | FALSE | 146.185 | @Lagnajee | 55.107 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/cdir.json) |
| cdww | FALSE | 34.159 | @Lagnajee | 7.188 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/cdww.json) |
| chnk | FALSE | 52.210 | @Lagnajee | 30.891 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/chnk.json) |
| ci | FALSE | 667.786 | @Lagnajee | 299.011 | absq meanabs 0.05 eb=8v | [json](../configs/era5/single/ci.json) |
| cin | FALSE | 53.901 | @Lagnajee | 44.145 | absq meanabs 1 eb=2v | [json](../configs/era5/single/cin.json) |
| cl | FALSE | 60.945 | @Lagnajee | 25.086 | absq meanrel 0.01 eb=11v*mean|x| | [json](../configs/era5/single/cl.json) |
| cp | FALSE | 141.655 | @Lagnajee | 34.535 | absq meanabs 1e-05 eb=8v | [json](../configs/era5/single/cp.json) |
| crr | FALSE | 34.228 | @Lagnajee | 22.816 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/crr.json) |
| csf | FALSE | 35194.576 | @Lagnajee | 541.844 | absq meanabs 1e-05 eb=256.0v | [json](../configs/era5/single/csf.json) |
| csfr | FALSE | 355.121 | @Lagnajee | 288.29 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/csfr.json) |
| cvh | FALSE | 95.230 | @Lagnajee | 26.389 | absq meanrel 0.01 eb=8v*mean|x| | [json](../configs/era5/single/cvh.json) |
| cvl | FALSE | 89.892 | @Lagnajee | 22.057 | absq meanrel 0.01 eb=11v*mean|x| | [json](../configs/era5/single/cvl.json) |
| dctb | FALSE | 38.977 | @Lagnajee | 26.86 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/dctb.json) |
| deg0l | FALSE | 21.151 | @Lagnajee | 15.556 | absq meanabs 1 eb=2v | [json](../configs/era5/single/deg0l.json) |
| dl | FALSE | 8.100 | @Lagnajee | 6.227 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/dl.json) |
| dndza | FALSE | 51.418 | @Lagnajee | 24.805 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/dndza.json) |
| dndzn | FALSE | 50.212 | @Lagnajee | 24.308 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/dndzn.json) |
| dwi | FALSE | 15.131 | @Lagnajee | 10.256 | absq meanabs 0.1 eb=2v | [json](../configs/era5/single/dwi.json) |
| dwps | FALSE | 43.685 | @Lagnajee | 29.903 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/dwps.json) |
| dwww | FALSE | 30.908 | @Lagnajee | 25.461 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/dwww.json) |
| e | FALSE | 23.308 | @Lagnajee | 11.711 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/e.json) |
| es | FALSE | 35194.576 | @Lagnajee | 3551.056 | absq meanabs 1e-05 eb=16v | [json](../configs/era5/single/es.json) |
| ewss | FALSE | 112.809 | @Lagnajee | 41.593 | absq meanabs 100 eb=2v | [json](../configs/era5/single/ewss.json) |
| fal | FALSE | 181.932 | @Lagnajee | 80.524 | absq meanabs 0.01 eb=2.8v | [json](../configs/era5/single/fal.json) |
| fdir | FALSE | 60.336 | @Lagnajee | 24.156 | absq meanabs 3600 eb=4v | [json](../configs/era5/single/fdir.json) |
| flsr | FALSE | 50.481 | @Lagnajee | 26.958 | absq meanrel 0.01 eb=1.4v*mean|x| | [json](../configs/era5/single/flsr.json) |
| fsr | FALSE | 60.107 | @Lagnajee | 14.443 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/fsr.json) |
| gwd | FALSE | 1916.456 | @Lagnajee | 230.4 | absq meanabs 1000 eb=16v | [json](../configs/era5/single/gwd.json) |
| hcc | FALSE | 31.753 | @Lagnajee | 18.226 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/hcc.json) |
| hmax | FALSE | 30.830 | @Lagnajee | 18.472 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/hmax.json) |
| i10fg | FALSE | 11.452 | @Lagnajee | 8.969 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/i10fg.json) |
| ie | FALSE | 23.608 | @Lagnajee | 11.822 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/ie.json) |
| iews | FALSE | 21.001 | @Lagnajee | 10.667 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/iews.json) |
| ilspf | FALSE | 27.071 | @Lagnajee | 15.703 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/ilspf.json) |
| inss | FALSE | 21.111 | @Lagnajee | 10.584 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/inss.json) |
| ishf | FALSE | 12.476 | @Lagnajee | 8.366 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/ishf.json) |
| isor | FALSE | 300.275 | @Lagnajee | 57.747 | absq meanabs 0.05 eb=5.6v | [json](../configs/era5/single/isor.json) |
| istl1 | FALSE | 5772.008 | @Lagnajee | 1807.206 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/istl1.json) |
| istl2 | FALSE | 6071.579 | @Lagnajee | 2021.889 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/istl2.json) |
| istl3 | FALSE | 7821.017 | @Lagnajee | 2909.254 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/istl3.json) |
| istl4 | FALSE | 34898.824 | @Lagnajee | 4979.568 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/istl4.json) |
| kx | FALSE | 18.969 | @Lagnajee | 11.584 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/kx.json) |
| lai_hv | FALSE | 80.123 | @Lagnajee | 20.854 | absq meanrel 0.01 eb=11v*mean|x| | [json](../configs/era5/single/lai_hv.json) |
| lai_lv | FALSE | 64.556 | @Lagnajee | 18.464 | absq meanrel 0.01 eb=8v*mean|x| | [json](../configs/era5/single/lai_lv.json) |
| lblt | FALSE | 337.283 | @Lagnajee | 140.379 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/lblt.json) |
| lcc | FALSE | 23.573 | @Lagnajee | 12.873 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/lcc.json) |
| lgws | FALSE | 34040.656 | @Lagnajee | 177.572 | absq meanabs 100 eb=256.0v | [json](../configs/era5/single/lgws.json) |
| licd | FALSE | 530.967 | @Lagnajee | 148.718 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/licd.json) |
| lict | FALSE | 1666.851 | @Lagnajee | 935.878 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/lict.json) |
| lmld | FALSE | 63.053 | @Lagnajee | 25.512 | absq meanabs 0.1 eb=5.6v | [json](../configs/era5/single/lmld.json) |
| lmlt | FALSE | 483.943 | @Lagnajee | 165.447 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/lmlt.json) |
| lsf | FALSE | 7550.836 | @Lagnajee | 208.075 | absq meanabs 1e-05 eb=64.0v | [json](../configs/era5/single/lsf.json) |
| lshf | FALSE | 138.529 | @Lagnajee | 105.767 | absq meanrel 0.01 eb=1.4v*mean|x| | [json](../configs/era5/single/lshf.json) |
| lsm | FALSE | 12.112 | @Lagnajee | 9.435 | lossless LZMA | [json](../configs/era5/single/lsm.json) |
| lsp | FALSE | 158.308 | @Lagnajee | 36.135 | absq meanabs 1e-05 eb=5.6v | [json](../configs/era5/single/lsp.json) |
| lspf | FALSE | 16.404 | @Lagnajee | 14.783 | relq pointwise 0.01 | [json](../configs/era5/single/lspf.json) |
| lsrr | FALSE | 35.623 | @Lagnajee | 22.902 | absq meanrel 0.01 eb=4v*mean|x| | [json](../configs/era5/single/lsrr.json) |
| lssfr | FALSE | 134.858 | @Lagnajee | 57.667 | absq meanrel 0.01 eb=8v*mean|x| | [json](../configs/era5/single/lssfr.json) |
| ltlt | FALSE | 432.195 | @Lagnajee | 148.596 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/ltlt.json) |
| mcc | FALSE | 27.752 | @Lagnajee | 14.055 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/mcc.json) |
| mdts | FALSE | 17.896 | @Lagnajee | 13.009 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/mdts.json) |
| mdww | FALSE | 17.216 | @Lagnajee | 11.858 | absq meanabs 0.1 eb=2v | [json](../configs/era5/single/mdww.json) |
| mgws | FALSE | 30536.471 | @Lagnajee | 184.273 | absq meanabs 100 eb=256.0v | [json](../configs/era5/single/mgws.json) |
| mn2t | FALSE | 21.572 | @Lagnajee | 17.491 | absq pointwise 0.05 | [json](../configs/era5/single/mn2t.json) |
| mntpr | FALSE | 28.931 | @Lagnajee | 17.907 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/mntpr.json) |
| mp1 | FALSE | 28.034 | @Lagnajee | 17.972 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/mp1.json) |
| mp2 | FALSE | 24.075 | @Lagnajee | 17.945 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/mp2.json) |
| mpts | FALSE | 24.029 | @Lagnajee | 18.209 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/mpts.json) |
| mpww | FALSE | 19.736 | @Lagnajee | 15.114 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/mpww.json) |
| msl | FALSE | 17.022 | @Lagnajee | 15.65 | absq meanabs 1 eb=1.0v | [json](../configs/era5/single/msl.json) |
| msqs | FALSE | 33.996 | @Lagnajee | 6.977 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/msqs.json) |
| mwd | FALSE | 19.787 | @Lagnajee | 13.548 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/mwd.json) |
| mwd1 | FALSE | 43.154 | @Lagnajee | 12.57 | absq meanrel 0.01 eb=1.4v*mean|x| | [json](../configs/era5/single/mwd1.json) |
| mwd2 | FALSE | 35.027 | @Lagnajee | 11.21 | absq meanrel 0.01 eb=1.4v*mean|x| | [json](../configs/era5/single/mwd2.json) |
| mwd3 | FALSE | 35.008 | @Lagnajee | 10.471 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/mwd3.json) |
| mwp | FALSE | 29.010 | @Lagnajee | 18.47 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/mwp.json) |
| mwp1 | FALSE | 43.767 | @Lagnajee | 14.856 | absq meanabs 0.01 eb=16v | [json](../configs/era5/single/mwp1.json) |
| mwp2 | FALSE | 37.781 | @Lagnajee | 13.531 | absq meanabs 0.01 eb=16v | [json](../configs/era5/single/mwp2.json) |
| mwp3 | FALSE | 18.006 | @Lagnajee | 12.33 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/mwp3.json) |
| mx2t | FALSE | 21.686 | @Lagnajee | 17.467 | absq pointwise 0.05 | [json](../configs/era5/single/mx2t.json) |
| mxtpr | FALSE | 23.481 | @Lagnajee | 13.144 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/mxtpr.json) |
| nsss | FALSE | 120.250 | @Lagnajee | 43.986 | absq meanabs 100 eb=2v | [json](../configs/era5/single/nsss.json) |
| p1ps | FALSE | 26.411 | @Lagnajee | 17.7 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/p1ps.json) |
| p1ww | FALSE | 23.221 | @Lagnajee | 15.942 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/p1ww.json) |
| p2ps | FALSE | 22.486 | @Lagnajee | 17.561 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/p2ps.json) |
| p2ww | FALSE | 23.651 | @Lagnajee | 15.243 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/p2ww.json) |
| pev | FALSE | 71.287 | @Lagnajee | 29.684 | absq meanrel 0.01 eb=8v*mean|x| | [json](../configs/era5/single/pev.json) |
| phiaw | FALSE | 25.210 | @Lagnajee | 12.094 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/phiaw.json) |
| phioc | FALSE | 24.760 | @Lagnajee | 14.674 | absq meanabs 0.03 eb=2v | [json](../configs/era5/single/phioc.json) |
| pp1d | FALSE | 28.937 | @Lagnajee | 18.433 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/pp1d.json) |
| ptype | FALSE | 178.445 | @Lagnajee | 167.691 | lossless int8 grid + LZMA | [json](../configs/era5/single/ptype.json) |
| rhoao | FALSE | 178.379 | @Lagnajee | 9.748 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/rhoao.json) |
| ro | FALSE | 14546.270 | @Lagnajee | 46.64 | absq meanabs 1e-05 eb=256.0v | [json](../configs/era5/single/ro.json) |
| rsn | FALSE | 702.047 | @Lagnajee | 581.037 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/rsn.json) |
| sd | FALSE | 1325.131 | @Lagnajee | 180.941 | absq meanrel 0.01 eb=16v*mean|x| | [json](../configs/era5/single/sd.json) |
| sdfor | FALSE | 45.064 | @Lagnajee | 39.215 | relq pointwise 0.05 | [json](../configs/era5/single/sdfor.json) |
| sdor | FALSE | 78.288 | @Lagnajee | 24.638 | absq meanabs 1 eb=5.6v | [json](../configs/era5/single/sdor.json) |
| sf | FALSE | 4002.853 | @Lagnajee | 174.19 | absq meanabs 1e-05 eb=45.0v | [json](../configs/era5/single/sf.json) |
| shts | FALSE | 32.008 | @Lagnajee | 21.966 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/shts.json) |
| shww | FALSE | 28.900 | @Lagnajee | 16.633 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/shww.json) |
| skt | FALSE | 19.575 | @Lagnajee | 16.203 | absq pointwise 0.05 | [json](../configs/era5/single/skt.json) |
| slhf | FALSE | 16.677 | @Lagnajee | 10.519 | absq meanabs 1000 eb=2v | [json](../configs/era5/single/slhf.json) |
| slor | FALSE | 35.891 | @Lagnajee | 26.505 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/slor.json) |
| slt | FALSE | 248.101 | @Lagnajee | 212.281 | lossless int8 grid + LZMA | [json](../configs/era5/single/slt.json) |
| smlt | FALSE | 35194.576 | @Lagnajee | 673.144 | absq meanabs 1e-05 eb=256.0v | [json](../configs/era5/single/smlt.json) |
| sp | FALSE | 201.390 | @Lagnajee | 102.818 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/sp.json) |
| src | FALSE | 563.190 | @Lagnajee | 39.19 | absq meanabs 1e-05 eb=16v | [json](../configs/era5/single/src.json) |
| sro | FALSE | 210.885 | @Lagnajee | 126.903 | absq meanrel 0.01 eb=32.0v*mean|x| | [json](../configs/era5/single/sro.json) |
| sshf | FALSE | 18.944 | @Lagnajee | 11.258 | absq meanabs 1000 eb=2v | [json](../configs/era5/single/sshf.json) |
| ssr | FALSE | 49.292 | @Lagnajee | 25.068 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/ssr.json) |
| ssrc | FALSE | 102.721 | @Lagnajee | 42.209 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/ssrc.json) |
| ssrd | FALSE | 51.175 | @Lagnajee | 25.166 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/ssrd.json) |
| ssrdc | FALSE | 147.522 | @Lagnajee | 54.497 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/ssrdc.json) |
| ssro | FALSE | 77.775 | @Lagnajee | 50.153 | absq meanrel 0.01 eb=11v*mean|x| | [json](../configs/era5/single/ssro.json) |
| sst | FALSE | 20.034 | @Lagnajee | 18.667 | absq meanabs 0.01 eb=1.0v | [json](../configs/era5/single/sst.json) |
| stl1 | FALSE | 310.223 | @Lagnajee | 134.485 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/stl1.json) |
| stl2 | FALSE | 313.265 | @Lagnajee | 143.639 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/stl2.json) |
| stl3 | FALSE | 351.410 | @Lagnajee | 146.442 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/stl3.json) |
| stl4 | FALSE | 341.554 | @Lagnajee | 140.702 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/stl4.json) |
| str | FALSE | 30.958 | @Lagnajee | 18.334 | absq meanabs 3600 eb=1.4v | [json](../configs/era5/single/str.json) |
| strc | FALSE | 62.762 | @Lagnajee | 31.037 | absq meanabs 3600 eb=2v | [json](../configs/era5/single/strc.json) |
| strd | FALSE | 39.707 | @Lagnajee | 21.5 | absq meanabs 3600 eb=2v | [json](../configs/era5/single/strd.json) |
| strdc | FALSE | 65.521 | @Lagnajee | 33.114 | absq meanabs 3600 eb=2v | [json](../configs/era5/single/strdc.json) |
| swh | FALSE | 42.905 | @Lagnajee | 23.377 | meanabs 0.01 SZ3 abs p=2.181 | [json](../configs/era5/single/swh.json) |
| swh1 | FALSE | 27.951 | @Lagnajee | 19.863 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/swh1.json) |
| swh2 | FALSE | 36.067 | @Lagnajee | 18.345 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/swh2.json) |
| swh3 | FALSE | 44.034 | @Lagnajee | 26.278 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/swh3.json) |
| swvl1 | FALSE | 55.769 | @Lagnajee | 13.637 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/swvl1.json) |
| swvl2 | FALSE | 54.551 | @Lagnajee | 12.264 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/swvl2.json) |
| swvl3 | FALSE | 53.771 | @Lagnajee | 12.251 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/swvl3.json) |
| swvl4 | FALSE | 62.323 | @Lagnajee | 14.819 | absq meanrel 0.01 eb=5.6v*mean|x| | [json](../configs/era5/single/swvl4.json) |
| tauoc | FALSE | 55.781 | @Lagnajee | 9.569 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/tauoc.json) |
| tcc | FALSE | 72.328 | @Lagnajee | 31.789 | absq meanabs 0.05 eb=2v | [json](../configs/era5/single/tcc.json) |
| tciw | FALSE | 356.661 | @Lagnajee | 63.3 | absq meanabs 0.01 eb=5.6v | [json](../configs/era5/single/tciw.json) |
| tclw | FALSE | 86.836 | @Lagnajee | 32.86 | absq meanabs 0.01 eb=2.8v | [json](../configs/era5/single/tclw.json) |
| tco3 | FALSE | 250.896 | @Lagnajee | 114.331 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/tco3.json) |
| tcrw | FALSE | 15129.180 | @Lagnajee | 82.235 | absq meanabs 0.01 eb=256.0v | [json](../configs/era5/single/tcrw.json) |
| tcslw | FALSE | 189.438 | @Lagnajee | 51.783 | absq meanabs 0.01 eb=4v | [json](../configs/era5/single/tcslw.json) |
| tcsw | FALSE | 282.485 | @Lagnajee | 53.052 | absq meanabs 0.01 eb=8v | [json](../configs/era5/single/tcsw.json) |
| tcw | FALSE | 28.919 | @Lagnajee | 18.004 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/tcw.json) |
| tcwv | FALSE | 29.301 | @Lagnajee | 18.203 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/tcwv.json) |
| tisr | FALSE | 334.336 | @Lagnajee | 79.283 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/tisr.json) |
| tmax | FALSE | 24.639 | @Lagnajee | 18.384 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/tmax.json) |
| totalx | FALSE | 24.486 | @Lagnajee | 15.976 | absq meanabs 0.1 eb=1.4v | [json](../configs/era5/single/totalx.json) |
| tp | FALSE | 69.075 | @Lagnajee | 25.71 | absq meanabs 1e-05 eb=4v | [json](../configs/era5/single/tp.json) |
| tplb | FALSE | 42.718 | @Lagnajee | 27.969 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/tplb.json) |
| tplt | FALSE | 39.518 | @Lagnajee | 26.754 | absq meanrel 0.01 eb=2.8v*mean|x| | [json](../configs/era5/single/tplt.json) |
| tsn | FALSE | 27.143 | @Lagnajee | 21.28 | absq pointwise 0.05 | [json](../configs/era5/single/tsn.json) |
| tsr | FALSE | 49.166 | @Lagnajee | 25.63 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/tsr.json) |
| tsrc | FALSE | 116.599 | @Lagnajee | 45.389 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/tsrc.json) |
| ttr | FALSE | 36.603 | @Lagnajee | 23.271 | absq meanabs 3600 eb=1.4v | [json](../configs/era5/single/ttr.json) |
| ttrc | FALSE | 75.471 | @Lagnajee | 44.179 | absq meanabs 3600 eb=1.4v | [json](../configs/era5/single/ttrc.json) |
| tvh | FALSE | 310.270 | @Lagnajee | 275.04 | lossless int8 grid + LZMA | [json](../configs/era5/single/tvh.json) |
| tvl | FALSE | 240.292 | @Lagnajee | 208.294 | lossless int8 grid + LZMA | [json](../configs/era5/single/tvl.json) |
| u10n | FALSE | 14.529 | @Lagnajee | 8.569 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/u10n.json) |
| ust | FALSE | 81.733 | @Lagnajee | 53.204 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/ust.json) |
| uvb | FALSE | 144.225 | @Lagnajee | 58.217 | absq meanabs 3600 eb=2.8v | [json](../configs/era5/single/uvb.json) |
| v10n | FALSE | 14.810 | @Lagnajee | 8.455 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/v10n.json) |
| vimd | FALSE | 13.276 | @Lagnajee | 8.301 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/vimd.json) |
| vst | FALSE | 99.658 | @Lagnajee | 49.707 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/vst.json) |
| wdw | FALSE | 59.900 | @Lagnajee | 43.771 | absq meanabs 0.01 eb=1.4v | [json](../configs/era5/single/wdw.json) |
| wind | FALSE | 16.412 | @Lagnajee | 12.491 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/wind.json) |
| wmb | FALSE | 42.034 | @Lagnajee | 38.391 | absq meanabs 0.1 eb=2.8v | [json](../configs/era5/single/wmb.json) |
| wsk | FALSE | 275.521 | @Lagnajee | 107.862 | absq meanabs 0.01 eb=2.8v | [json](../configs/era5/single/wsk.json) |
| wsp | FALSE | 34.923 | @Lagnajee | 17.883 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/wsp.json) |
| wss | FALSE | 40.052 | @Lagnajee | 11.314 | relq meanrel 0.01 ratio=1+1.9v | [json](../configs/era5/single/wss.json) |
| wstar | FALSE | 33.782 | @Lagnajee | 20.713 | absq meanabs 0.01 eb=2v | [json](../configs/era5/single/wstar.json) |
| z | FALSE | 23.634 | @Lagnajee | 16.933 | absq pointwise 10 | [json](../configs/era5/single/z.json) |
| zust | FALSE | 27.666 | @Lagnajee | 15.166 | absq meanrel 0.01 eb=2v*mean|x| | [json](../configs/era5/single/zust.json) |
