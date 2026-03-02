# %% [markdown]
# # This script is to download CMIP6 data using intake-esm library
#
# Read more from link
#
# https://intake-esm.readthedocs.io/en/stable/tutorials/loading-cmip6-data.html
#
# How to use intake to download GCM
#

# %%
import concurrent.futures
import os
from pathlib import Path

import intake
import numpy as np
import pandas as pd
import util
import xarray as xr
from tqdm.autonotebook import tqdm
from util import PANGEO_CATALOG_URL


# %%
def download_files(
    download_dir: Path, catalog_url: str, sid: str, exp: str, var: str, start_year: int, end_year: int
):
    """
    Download files from the CMIP6 data store

    :param download_dir: directory to save downloaded files
    :param catalog_url: intake esm data store
    :param sid: source_id
    :param exp: experiment_id
    :param var: variable_id
    """

    catalog = intake.open_esm_datastore(catalog_url)
    models = catalog.search(
        experiment_id=exp,
        table_id="Amon",
        variable_id=var,
        source_id=sid,
    )
    # then one might get several files with the same conditions
    # r1: Realization (initial condition run)
    # i1: Initialization method
    # p1: Physical parameters
    # f1: External forcings

    # if no files exist then print out error
    if len(models.df) == 0:
        print("*** No data found for", var, exp, sid)
        return False

    member_ids = util.natural_sort(models.df.member_id.values)

    # get the first one only then seach again
    first_member_id = member_ids[0]
    first_member = catalog.search(
        experiment_id=exp,
        table_id="Amon",
        variable_id=var,
        source_id=sid,
        member_id=first_member_id,
    )

    # if no files exist then print out error
    if len(first_member.df) == 0:
        print(
            "*** This is impossible, there must be data for",
            var,
            exp,
            sid,
            member_ids[0],
        )
        return False

    odir = download_dir / sid / exp
    odir.mkdir(parents=True, exist_ok=True)

    def output_file_name(key):
        return odir / f"{var}_{key}_{first_member_id}_{start_year}_{end_year}.nc"

    try:
        # If all output files exist, skip
        if all((output_file_name(key)).exists() for key in first_member.keys()):
            return True

        datasets: dict[str, xr.Dataset] = first_member.to_dataset_dict(
            xarray_open_kwargs={"consolidated": True},
            storage_options={"asynchronous": False},
            progressbar=False,
        )

        use_historical = exp != "historical" and start_year <= 2014 and end_year >= 2015
        if use_historical:
            historical_member = catalog.search(
                experiment_id="historical",
                table_id="Amon",
                variable_id=var,
                source_id=sid,
                member_id=first_member_id,
            )
            historical_datasets: dict[str, xr.Dataset] = historical_member.to_dataset_dict(
                xarray_open_kwargs={"consolidated": True},
                storage_options={"asynchronous": False},
                progressbar=False,
            )
            historical_by_present_key = {
                historical_key: historical_ds
                for historical_key, historical_ds in historical_datasets.items()
            }

        for i, (key, ds) in enumerate(datasets.items()):
            # Must use isin because some dataset has time variable not monotonically increasing
            if use_historical:
                historical_data = list(historical_by_present_key.values())[i].sel(
                    time=list(historical_by_present_key.values())[i].time.dt.year.isin(np.arange(start_year, 2014 + 1))
                )
                present_data = ds.sel(
                    time=ds.time.dt.year.isin(np.arange(2015, end_year + 1))
                )
                year_data = xr.concat([historical_data, present_data], dim="time").sortby("time")
            else:
                year_data = ds.sel(
                    time=ds.time.dt.year.isin(np.arange(start_year, end_year + 1))
                )

            years = np.unique(year_data.time.dt.year.values)

            if len(years) == 0:
                print(
                    f"{sid}, {exp}, {var}, requested {start_year}-{end_year} data but no data found"
                )
                return False

            if years[0] != start_year or years[-1] != end_year:
                print(
                    f"{sid}, {exp}, {var}, requested {start_year}-{end_year} data "
                    f"but only {years[0]}-{years[-1]} data found"
                )
                return False

            month_mean = year_data.groupby("time.month").mean("time").squeeze(drop=True)

            ofile = output_file_name(key)
            tmp_ofile = ofile.with_suffix(ofile.suffix + ".tmp")

            # Save to temporary file first, and then rename to output file to
            # avoid regarding corrupted file due to sudden termination as
            # complete file.
            util.to_netcdf(month_mean, tmp_ofile)
            tmp_ofile.rename(ofile)

    except Exception as e:
        print("*** Couldn't download", var, exp, sid, e)
        return False

    return True


# %%
# Example usage
# download_files(CATALOG_URL, "EC-Earth3", "historical", "tas", 1995, 2014)
# download_files(CATALOG_URL, "EC-Earth3", "historical", "ta", 1995, 2014)
# download_files(CATALOG_URL, "MPI-ESM1-2-HR", "historical", "tas", 1995, 2014)


# %%
def download_data(
    download_dir: Path,
    source_ids: list[str],
    experiments: list[str],
    variables: list[str],
    start_year: int,
    end_year: int,
):
    status = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        status = []
        for sid in source_ids:
            for exp in experiments:
                for var in variables:
                    future = executor.submit(
                        download_files,
                        download_dir,
                        PANGEO_CATALOG_URL,
                        sid,
                        exp,
                        var,
                        start_year,
                        end_year,
                    )
                    futures.append(future)
                    status.append(
                        {
                            "source_id": sid,
                            "experiment": exp,
                            "variable": var,
                        }
                    )

        for future, stat in tqdm(zip(futures, status), total=len(futures)):
            try:
                success = future.result()
            except Exception as e:
                success = False
                print("*** Error:", e)

            stat["success"] = success

    return pd.DataFrame(status)


# %%
if __name__ == "__main__":
    #  Please modify the settings to include the models you want to download
    source_ids = [
        "EC-Earth3",
        "MIROC6",
        "MRI-ESM2-0",
        "ACCESS-CM2",
        "IPSL-CM6A-LR",
        "MPI-ESM1-2-HR",
    ]
    experiments = ['ssp585', 'ssp126', 'ssp370', 'ssp245']
    variables = ["tas", "ta", "ua", "va", "hur", "zg", "ts"]
    # historical_period = (1991, 2014)
    present_period = (1991, 2020)
    ssp_period = (2071, 2100)
    download_dir = Path(os.getenv("CMIP6"))
    download_dir.mkdir(parents=True, exist_ok=True)

    # historical_status = download_data(download_dir, source_ids, ["historical"], variables, *historical_period)
    present_status = download_data(download_dir, source_ids, experiments, variables, *present_period)
    ssp_status = download_data(download_dir, source_ids, experiments, variables, *ssp_period)

    download_status = pd.concat([present_status, ssp_status], ignore_index=True)
    print(f"Successfully downloaded {download_status['success'].sum()} files")

    failed_download = download_status.query("~success")
    if not failed_download.empty:
        print("Couldn't download the following files")
        print(failed_download)
    else:
        print("No failed download")
