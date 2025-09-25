# %%
import logging
import struct
from pathlib import Path
from typing import IO

import numpy as np
import pandas as pd
import xarray as xr

_logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


class FileInventory:
    def __init__(self):
        self._files = {}

    def get(self, filename: Path):
        if filename not in self._files:
            self._files[filename] = open(filename, "wb")
        return self._files[filename]

    def close_all(self):
        for fp in self._files.values():
            fp.close()
        self._files = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_all()


# %%
def write_fortran_record(fp: IO, data):
    data = np.array(data)
    data = np.array(data, dtype=data.dtype.newbyteorder(">"))
    nbytes = data.nbytes
    fp.write(struct.pack(">i", nbytes))
    fp.write(data.tobytes(order="F"))
    fp.write(struct.pack(">i", nbytes))


def pad(s: str, length: int) -> bytes:
    """Pad string to fixed length with spaces and convert to bytes."""
    return s.ljust(length)[:length].encode("ascii")


def to_wps_interm(
    data: xr.DataArray,
    var_name: str,
    prefix: str,
    file_inventory: FileInventory,
    time: pd.Timestamp = None,
):
    """Convert xarray DataArray to WPS intermediate file format.

    Reference: https://www2.mmm.ucar.edu/wrf/OnLineTutorial/Basics/IM_files/IM_wps.php
    """

    if time is None:
        time = pd.Timestamp(data.time.values)

    if hasattr(data, "plev"):
        plev = data.plev.values
    else:
        plev = 200100  # surface

    filename = f"{prefix}:{time.strftime('%Y-%m-%d_%H')}"
    fp = file_inventory.get(filename)

    # Fill missing values by linear interpolation
    data = data.interpolate_na(
        "lat", method="linear", fill_value="extrapolate", keep_attrs=True
    )
    data = data.interpolate_na(
        "lon", method="linear", fill_value="extrapolate", keep_attrs=True
    )

    # Write IFV
    write_fortran_record(fp, struct.pack(">i", 5))

    # Write HDATE, XFCST, MAP_SOURCE, FIELD, UNITS, DESC, XLVL, NX, NY, IPROJ
    write_fortran_record(
        fp,
        struct.pack(
            ">24sf32s9s25s46sfiii",
            pad(time.strftime("%Y-%m-%d_%H:00:00"), 24),  # HDATE
            0.0,  # XFCST
            pad("CMIP6", 32),  # MAP_SOURCE
            pad(var_name, 9),  # FIELD
            pad(data.units, 25),  # UNITS
            pad(data.standard_name, 46),  # DESC
            plev,  # XLVL
            len(data.coords["lon"]),  # NX
            len(data.coords["lat"]),  # NY
            0,  # IPROJ
        ),
    )

    # Write STARTLOC, STARTLAT, STARTLON, DELTALAT, DELTALON, EARTH_RADIUS
    write_fortran_record(
        fp,
        struct.pack(
            ">8s5f",
            pad("SWCORNER", 8),  # STARTLOC
            data.coords["lat"][0],  # STARTLAT
            data.coords["lon"][0],  # STARTLON
            data.coords["lat"][1] - data.coords["lat"][0],  # DELTALAT
            data.coords["lon"][1] - data.coords["lon"][0],  # DELTALON
            6367470e-3,  # EARTH_RADIUS
        ),
    )

    # Write IS_WIND_EARTH_REL
    write_fortran_record(fp, struct.pack(">i", 0))  # IS_WIND_EARTH_REL

    # Write SLAB
    write_fortran_record(fp, data.transpose("lon", "lat").values.astype(">f4"))


# %%
def convert_single_file(
    nc_file: Path,
    model_conf: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    interval: pd.Timedelta,
    prefix: str,
    file_inventory: FileInventory,
):
    _logger.info("Processing file %s", nc_file)
    ds = xr.open_dataset(nc_file)

    if "time" in ds.dims:
        ds = ds.sel(time=slice(start_date, end_date))
        if ds.sizes["time"] == 0:
            _logger.info("No data in %s for the given time range", nc_file)
            return

        _logger.info("  Selecting necessary time steps")
        ds = ds.sel(time=pd.date_range(start_date, end_date, freq=interval))

    for var_name in ds.variables.keys():
        out_vars = model_conf[model_conf["var_id"] == var_name]
        if len(out_vars) == 0:
            continue

        data = ds[var_name]
        for _, var_conf in out_vars.iterrows():
            _logger.info(
                "Processing variable %s in %s to yield %s",
                var_name,
                nc_file,
                var_conf["wps_name"],
            )

            if np.isfinite(var_conf["scale"]):
                _logger.info(
                    "  Applying scale factor %s and units %s",
                    var_conf["scale"],
                    var_conf["units"],
                )
                with xr.set_options(keep_attrs=True):
                    data = data * float(var_conf["scale"])
                data.attrs["units"] = var_conf["units"]

            if data.attrs["units"] != var_conf["units"]:
                _logger.critical(
                    "  Units mismatch for variable %s: data has %s but expected %s",
                    var_name,
                    data.attrs["units"],
                    var_conf["units"],
                )
                raise ValueError("Units mismatch")

            if "time" in ds.dims:
                if "plev" in ds.dims:
                    _logger.info(
                        "  This is a pressure level data with levels: %s",
                        data.plev.values,
                    )
                else:
                    _logger.info("  This is a surface data")
                for i_time in range(len(data.time)):
                    if "plev" in data.dims:
                        for i_plev in range(len(data.plev)):
                            to_wps_interm(
                                data.isel(time=i_time, plev=i_plev),
                                var_conf["wps_name"],
                                prefix,
                                file_inventory=file_inventory,
                            )
                    else:
                        to_wps_interm(
                            data.isel(time=i_time),
                            var_conf["wps_name"],
                            prefix,
                            file_inventory=file_inventory,
                        )
            else:
                _logger.info("  This is a static surface data")
                for time in pd.date_range(start_date, end_date, freq=interval):
                    to_wps_interm(
                        data,
                        var_conf["wps_name"],
                        prefix,
                        time=time,
                        file_inventory=file_inventory,
                    )

    ds.close()


model_conf = pd.read_csv("model_conf/MIROC6.csv")
start_date = pd.Timestamp("2010-01-05")
end_date = pd.Timestamp("2010-01-06")

with FileInventory() as file_inventory:
    for data_file in Path("Download_6hr").glob("*MIROC6_historical*.nc"):
        convert_single_file(
            data_file,
            model_conf,
            start_date,
            end_date,
            pd.Timedelta(hours=6),
            "MIROC6_HISTORICAL",
            file_inventory,
        )
