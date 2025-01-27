"""Create PGW WRF intermediate files"""

# %%
import logging
from pathlib import Path

import numpy as np
import pywinter.winter as pyw
import xarray as xr
import xesmf as xe
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# %%
# A map from WPS intermediate variable name to CMIP6 variable name
VAR_MAP = {
    "RH": "hur",
    "TT": "ta",
    "UU": "ua",
    "VV": "va",
    "GHT": "zg",
    "SKINTEMP": "ts",
    "SST": "ts",
}


def target_dataset(wps_inter_filepath):
    wps_inter_ds = pyw.rinter(wps_inter_filepath)

    # Temperature must be present in the WPS intermediate file
    tt_var = wps_inter_ds["TT"]

    tt_geoproj = tt_var.geoinfo
    plev = tt_var.level
    lat = (
        np.arange(tt_var.val.shape[-2]) * tt_geoproj["DELTALAT"]
        + tt_geoproj["STARTLAT"]
    )
    lon = (
        np.arange(tt_var.val.shape[-1]) * tt_geoproj["DELTALON"]
        + tt_geoproj["STARTLON"]
    )
    ds_target = xr.Dataset(coords={"lat": lat, "lon": lon})

    metadata = {
        "nlat": len(lat),
        "nlon": len(lon),
        "startlat": tt_geoproj["STARTLAT"],
        "startlon": tt_geoproj["STARTLON"],
        "deltalat": tt_geoproj["DELTALAT"],
        "deltalon": tt_geoproj["DELTALON"],
        "plev": plev,
    }

    return ds_target, plev, metadata


def calculate_deltas(
    ds_target,
    plev,
    source_ids,
    experiment,
    present,
    future,
    download_dir,
    variables=["ta", "ua", "va", "hur", "zg", "ts"],
) -> xr.Dataset:
    present = present.replace("-", "_")
    future = future.replace("-", "_")

    deltas = {}

    pbar = tqdm(desc="Calculating deltas", total=len(variables) * len(source_ids))

    for variable in variables:
        diffs = []
        for source_id in source_ids:
            pbar.set_postfix_str(f"{variable}, {source_id}")

            present_dir = download_dir / source_id / "historical"
            (present_file,) = present_dir.glob(f"{variable}_*{present}.nc")
            present_ds = xr.open_dataset(present_file)[variable]

            future_dir = download_dir / source_id / experiment
            (future_file,) = future_dir.glob(f"{variable}_*{future}.nc")
            future_ds = xr.open_dataset(future_file)[variable]

            diff = future_ds - present_ds

            regridder = xe.Regridder(diff, ds_target, "bilinear")

            diff = regridder(diff)
            if "plev" in diff.dims:
                diff = diff.interp(plev=plev)

            diffs.append(diff)

            pbar.update(1)

        mean_diff = diffs[0].copy(data=np.nanmean(diffs, axis=0))
        mean_diff = mean_diff.fillna(0)

        deltas[variable] = mean_diff.astype(np.float32)

    pbar.close()

    return xr.Dataset(deltas)


def apply_pgw_delta(wps_inter_filepath, deltas, dst_dir, var_map):
    prefix, date = wps_inter_filepath.name.split(":")
    month = int(date.split("-")[1])

    _logger.info(f"Processing {wps_inter_filepath}")
    inter_ds = pyw.rinter(wps_inter_filepath)

    varnames = list(inter_ds.keys())

    var = inter_ds[varnames[0]]
    geoinfo = pyw.Geo0(
        var.geoinfo["STARTLAT"],
        var.geoinfo["STARTLON"],
        var.geoinfo["DELTALAT"],
        var.geoinfo["DELTALON"],
    )

    fields = []

    for varname in varnames:
        _logger.debug(f"Processing {varname}")
        var = inter_ds[varname]
        values = var.val

        # Apply PGW delta
        if varname in ["TT", "UU", "VV", "GHT", "SKINTEMP", "SST"]:
            gwi_val = deltas[var_map[varname]].sel(month=month).values
            values = values + gwi_val

        if varname in ["SM", "ST", "SOILM", "SOILT"]:  # soil variables
            field = pyw.Vsl(varname, values, var.level)
        elif isinstance(var.level, str):  # 2D variables
            out_varname = varname
            if varname.endswith("2M"):
                out_varname = varname[:-2]
            elif varname.endswith("10M"):
                out_varname = varname[:-3]
            field = pyw.V2d(
                out_varname,
                values,
                var.general["DESC"],
                var.general["UNITS"],
                var.general["XLVL"],
            )
        else:
            field = pyw.V3dp(varname, values, var.level)

        fields.append(field)

    _logger.info(f"Writing to {dst_dir}/{prefix}_{date}")
    pyw.cinter(prefix, date, geoinfo, fields, dst_dir)


# %%
def verify_metadata(metadata, cache_attributes):
    for key in metadata:
        if key not in cache_attributes:
            return False

        value = metadata[key]
        other = cache_attributes[key]

        # Check if is list,
        if isinstance(value, (list, np.ndarray)):
            if len(value) == 1:
                value = value[0]
            if np.any(value != other):
                return False
        # Check if is float
        elif isinstance(value, (np.floating, float)):
            if not np.isclose(value, other):
                return False
        # Compare directly
        elif value != other:
            return False

    return True


# %%
src_dir = Path("/data7/khanhdn/wrf/WPS/runs/era5_test/")
dst_dir = "/data7/khanhdn/wrf/WPS/runs/era5_test_pgw/"
wps_inter_prefix = "ERA5"
# Calculating deltas sometimes takes a long time so we can cache the result to a
# file if necessary, set it to None to disable caching
cache_file = "era5_cache.nc"

# src_dir = Path("/data7/khanhdn/wrf/WPS/met_input/FNL/ungrib")
# dst_dir = "/data7/khanhdn/wrf/WPS/runs/fnl_test_pgw/"
# wps_inter_prefix = "FNL"
# cache_file = "fnl_cache.nc"

wps_inter_filepaths = list(src_dir.glob(f"{wps_inter_prefix}:*"))

present = "1995-2014"
future = "2045-2064"
source_ids = [
    "EC-Earth3",
    "MIROC6",
    "MRI-ESM2-0",
    "ACCESS-CM2",
    "IPSL-CM6A-LR",
    "MPI-ESM1-2-HR",
]
experiment = "ssp585"
download_dir = Path("Download_CMIP6/Download")

ds_target, plev, metadata = target_dataset(wps_inter_filepaths[0])

metadata.update(
    {
        "source_ids": sorted(source_ids),
        "experiment": experiment,
        "present": present,
        "future": future,
    }
)

# %%
if cache_file is not None and Path(cache_file).exists():
    _logger.info(f"Reading cache file {cache_file}")
    deltas = xr.open_dataset(cache_file)
    if not verify_metadata(metadata, deltas.attrs):
        message = (
            "Cache metadata mismatch. "
            "Maybe the cache file was created with "
            "different parameters (e.g., GCMs, experiment, years)."
        )
        _logger.critical(message + f"\nExpected: {metadata}\nActual: {deltas.attrs}")
        raise RuntimeError(message)
    _logger.info("Cache file read successfully")
else:
    _logger.info("Calculating deltas")
    deltas = calculate_deltas(
        ds_target,
        plev,
        source_ids,
        experiment,
        present,
        future,
        download_dir,
    )

# %%
# Write cache if the cache file does not exist
if cache_file is not None and not Path(cache_file).exists():
    _logger.info(f"Writing cache file {cache_file}")
    deltas.attrs.update(metadata)
    deltas.to_netcdf(
        cache_file,
        encoding={
            varname: {"zlib": True, "complevel": 1} for varname in deltas.variables
        },
    )


# %%
if not Path(dst_dir).exists():
    _logger.info(f"Creating directory {dst_dir} for the output files")
    Path(dst_dir).mkdir(parents=True)

for wps_inter_filepath in wps_inter_filepaths:
    apply_pgw_delta(wps_inter_filepath, deltas, dst_dir, VAR_MAP)
