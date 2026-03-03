import re
from pathlib import Path
from typing import Iterable

import netcdf_util
import xarray as xr

# PANGEO_CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
# GLADE_CATALOG_URL = "https://raw.githubusercontent.com/NCAR/intake-esm-datastore/refs/heads/main/catalogs/glade-cmip6.json"
PANGEO_CATALOG_URL = "https://raw.githubusercontent.com/NCAR/intake-esm-datastore/master/catalogs/pangeo-cmip6.json"

def natural_sort(arr: Iterable[str], /) -> list[str]:
    """
    Sort names like r1i1p1f1, r1i2p1f1 in a natural (numeric) order.
    - r1: Realization (initial condition run),
    - i1: Initialization method,
    - p1: Physical parameters,
    - f1: External forcings.

    Numeric order means that r1i1p1f1 < r2i1p1f1 < r11i1p1f1.

    :param l: list of names to be sorted
    """

    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return tuple(convert(c) for c in re.split(r"(\d+)", key))

    return sorted(arr, key=alphanum_key)


def to_netcdf(ds: xr.Dataset, ofile: str | Path):
    """
    Write an xarray dataset to a netCDF file.

    :param ds: xarray dataset
    :param ofile: output file name
    """
    encoding = {
        var_name: {
            "zlib": True,
            "complevel": 1,
            "chunksizes": netcdf_util.chunk_shape_nD(data.shape, chunkSize=64 * 2**10),
        }
        for var_name, data in ds.data_vars.items()
    }

    # Save to temporary file first, and then rename to output file to
    # avoid regarding corrupted file due to sudden termination as
    # complete file.
    ds.to_netcdf(ofile, format="NETCDF4_CLASSIC", engine="netcdf4", encoding=encoding)
