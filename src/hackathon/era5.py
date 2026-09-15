"""ERA5 challenges (04 pressure-level, 05 single-level).

The data loader is copied from the "Challenge Configuration (do not edit)" cell
of `04-challenges/04-era5-pressure.ipynb`. Fields are streamed from GRIB files
on the ESiWACE S3 bucket via kerchunk references and cached locally as `.npy`.
Scoring uses the official `compression_requirement_checks.check_safety_requirements`,
exactly as the notebooks do.
"""

import contextlib
import io
import json
import time
from functools import cache
from pathlib import Path
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
import xarray as xr

from .challenges import DATA, Result

BASE_URL = "https://object-store.os-api.cci1.ecmwf.int/esiwacebucket"
TIME = "2026-07-15T12:00:00"
CACHE = DATA / "era5"

ERA5_SOURCES = {
    "pressure": {
        "ref_url": f"{BASE_URL}/ERA5_07_2026/era5_pressure_50_500_850_1000_202607_3h.grib.ref",
        "catalog_url": f"{BASE_URL}/ERA5_07_2026/era5_pressure_50_500_850_1000_202607_3h.grib.refs.json",
    },
    "single": {
        "catalog_url": f"{BASE_URL}/ERA5_07_2026/era5_single_202607_6h.grib.refs.json",
    },
}

LEADERBOARD_ISSUE = {"pressure": 56, "single": 57}


def _as_list(value):
    if value is None or isinstance(value, (str, bytes)):
        return [value]
    return list(value)


def _load_json(location):
    if str(location).startswith(("http://", "https://")):
        response = requests.get(location)
        response.raise_for_status()
        return response.json()
    return json.loads(Path(location).read_text())


@cache
def load_catalog(leveltype: str) -> dict:
    return _load_json(ERA5_SOURCES[leveltype]["catalog_url"])


def _var_name(ds, param):
    aliases = {"2t": "t2m", "2d": "d2m", "10u": "u10", "10v": "v10"}
    for name in (param, aliases.get(param)):
        if name in ds.data_vars:
            return name
    return None


def _open_ref(ref_location):
    ref = _load_json(ref_location)
    return xr.open_dataset(
        "reference://",
        engine="zarr",
        backend_kwargs={
            "storage_options": {
                "fo": ref,
                "asynchronous": True,
                "remote_options": {"asynchronous": True},
            }
        },
        consolidated=False,
        chunks={},
    )


def _subset(ds, params):
    names = [_var_name(ds, name) for name in params]
    missing = [param for param, name in zip(params, names) if name is None]
    if missing:
        raise KeyError(f"Variable(s) {missing} not found. Available: {list(ds.data_vars)}")
    return ds[names]


def load_era5_data(leveltype: str, param: str) -> xr.Dataset:
    params = _as_list(param)
    source = ERA5_SOURCES[leveltype]
    if "ref_url" in source:
        return _subset(_open_ref(source["ref_url"]), params)
    catalog = load_catalog(leveltype)
    for group in catalog["groups"].values():
        group_params = [p for p in params if p in set(group.get("variables", []))]
        if group_params:
            ref = group["ref"]
            location = ref if str(ref).startswith(("http://", "https://")) else urljoin(source["catalog_url"], ref)
            return _subset(_open_ref(location), group_params)
    raise ValueError(f"Parameter {param!r} not found in the {leveltype} catalog")


def variables(leveltype: str) -> list[str]:
    catalog = load_catalog(leveltype)
    return sorted({v for group in catalog["groups"].values() for v in group["variables"]})


def field(leveltype: str, var: str) -> np.ndarray:
    """The challenge's test field (one timestep), cached locally."""
    path = CACHE / f"{leveltype}_{var}.npy"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        ds = load_era5_data(leveltype, var)
        np.save(path, ds[_var_name(ds, var)].sel(time=pd.Timestamp(TIME)).values)
    return np.load(path)


def requirements(leveltype: str, var: str) -> list:
    from compression_recommendations import Recommendations

    return list(
        Recommendations.provide.search(markers={"grib-short-name": var, "level-kind": leveltype})
    )


def evaluate(codec, leveltype: str, var: str) -> Result:
    """Encode, decode, and score with the official safety requirement checks."""
    from compression_requirement_checks import check_safety_requirements

    x = field(leveltype, var)
    reqs = requirements(leveltype, var)
    t = time.perf_counter()
    enc = codec.encode(x)
    dec = np.asarray(codec.decode(enc)).reshape(x.shape)
    dt = time.perf_counter() - t
    with contextlib.redirect_stdout(io.StringIO()):
        ok = bool(check_safety_requirements(original=x, reconstructed=dec, requirements=reqs))
    # the ERA5 notebooks report pass/fail rather than a violation fraction
    return Result(x.nbytes / np.array(enc).nbytes, 0.0 if ok else 1.0, dt)
