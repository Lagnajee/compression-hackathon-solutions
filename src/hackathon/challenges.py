"""Challenge definitions mirroring the "do not edit" cells of the lab notebooks.

The data selection, violation formula, and compression ratio are copied
verbatim from `04-challenges/0[1-3]-*.ipynb` in
https://github.com/climet-eu/compression-lab-notebooks. Only the data source
differs: the notebooks stream the files through the in-browser `ipyfilite`,
while we read byte-identical local copies (see `scripts/download_data.sh`).
"""

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get("HACKATHON_DATA", ROOT / "data"))


@dataclass(frozen=True)
class Result:
    compression_ratio: float
    violations: float
    seconds: float

    @property
    def ok(self) -> bool:
        return self.violations == 0


@dataclass(frozen=True)
class Challenge:
    key: str
    name: str
    leaderboard_issue: int
    load: Callable[[], xr.DataArray]
    evaluate: Callable[[object, xr.DataArray], Result]


def _open(name: str) -> xr.Dataset:
    return xr.open_dataset(
        DATA / name, engine="h5netcdf", decode_timedelta=True, cache=False
    )


# ------------------------------------------------------------------ 01
def _load_01() -> xr.DataArray:
    return _open("hoaps.nc")["wvpa"].sel(time=slice("2020-08-01", "2020-08-07")).load()


def _eval_01(codec, da: xr.DataArray) -> Result:
    eb_abs_check = 1  # kg m-2
    t = time.perf_counter()
    da_enc = codec.encode(da.values)
    da_dec = da.copy(data=codec.decode(da_enc, out=np.empty(da.shape, dtype=da.dtype)))
    dt = time.perf_counter() - t
    # violation if (a) the absolute error bound is exceeded
    #  or (b) missing NaN values are not preserved
    violations = np.mean(
        xr.where(
            np.isnan(da),
            ~np.isnan(da_dec),
            ~(np.abs(da_dec - da) <= eb_abs_check),
        )
    )
    return Result(da.nbytes / np.array(da_enc).nbytes, float(violations), dt)


# ------------------------------------------------------------------ 02
def _load_02() -> xr.DataArray:
    return _open("tp.nc")["tp"].load()


def _eval_02(codec, da: xr.DataArray) -> Result:
    eb_rel_check = 0.01  # 1%
    t = time.perf_counter()
    da_enc = codec.encode(da.values)
    da_dec = da.copy(data=codec.decode(da_enc))
    dt = time.perf_counter() - t
    # violation if the relative error bound is exceeded (incl. if zero is not preserved)
    violations = np.mean(~(np.abs(da_dec - da) <= (np.abs(da) * eb_rel_check)))
    return Result(da.nbytes / np.array(da_enc).nbytes, float(violations), dt)


# ------------------------------------------------------------------ 03
def _load_03() -> xr.DataArray:
    return _open("hus.nc")["hus"].load()


def differentiate_along_longitude(da: xr.DataArray) -> xr.DataArray:
    # copied verbatim from the notebook; note that the denominator evaluates to
    # (lon[i-5] - lon[i+5]) % 360 = 357.5 degrees, not the intended 2.5 degrees
    return (da.roll(lon=5) - da.roll(lon=-5)) / (
        np.mod(da.lon.roll(lon=5) - da.lon.roll(lon=-5), 360)
    )


def _eval_03(codec, da: xr.DataArray) -> Result:
    eb_abs_qoi_check = 1e-6
    t = time.perf_counter()
    da_enc = codec.encode(da.values)
    da_dec = da.copy(data=codec.decode(da_enc))
    dt = time.perf_counter() - t
    da_deriv = differentiate_along_longitude(da)
    da_dec_deriv = differentiate_along_longitude(da_dec)
    violations = np.mean(~(np.abs(da_dec_deriv - da_deriv) <= eb_abs_qoi_check))
    return Result(da.nbytes / np.array(da_enc).nbytes, float(violations), dt)


CHALLENGES = {
    c.key: c
    for c in [
        Challenge("01-nan-missing-values", "Missing Values", 47, _load_01, _eval_01),
        Challenge("02-relative-error-bound", "Pointwise Relative Error Bound", 48, _load_02, _eval_02),
        Challenge("03-spatial-gradient", "Absolute Error Bound over Spatial Gradient", 49, _load_03, _eval_03),
    ]
}
