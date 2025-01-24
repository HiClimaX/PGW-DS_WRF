"""Create PGW WRF intermediate files"""

# %%
from pathlib import Path

import numpy as np
import pywinter.winter as pyw
import xarray as xr
import xesmf as xe
from tqdm import tqdm

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

    return ds_target, plev


def calculate_deltas(
    ds_target,
    plev,
    source_ids,
    experiment,
    present,
    future,
    download_dir,
    variables=["ta", "ua", "va", "hur", "zg", "ts"],
):
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

        deltas[variable] = mean_diff

    pbar.close()

    return deltas


def apply_pgw_delta(wps_inter_filepath, deltas, dst_dir, var_map):
    prefix, date = wps_inter_filepath.name.split(":")
    month = int(date.split("-")[1])

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

    pyw.cinter(prefix, date, geoinfo, fields, dst_dir)


# %%
src_dir = Path("/data7/khanhdn/wrf/WPS/runs/era5_test/")
dst_dir = "/data7/khanhdn/wrf/WPS/runs/era5_test_pgw/"
wps_inter_prefix = "ERA5"

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

ds_target, plev = target_dataset(wps_inter_filepaths[0])

# %%
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
for wps_inter_filepath in wps_inter_filepaths:
    apply_pgw_delta(wps_inter_filepath, deltas, dst_dir, VAR_MAP)
