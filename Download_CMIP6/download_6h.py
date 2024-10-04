# %%
import os
import re
from operator import itemgetter

import intake
import numpy as np
import pandas as pd
import pyesgf.search
import util
import xarray as xr
from pyesgf.search import SearchConnection
from util import PANGEO_CATALOG_URL, natural_sort

# %%

conn = SearchConnection("https://esgf.ceda.ac.uk/esg-search", distrib=True)
facets = "project,experiment_id,variable_id,source_id,member_id,table_id,frequency"

# %%
start_date = pd.Timestamp("2010-01-01")
end_date = pd.Timestamp("2010-02-01")

# %%
ctx = conn.new_context(
    project="CMIP6",
    experiment_id="historical",
    variable="ta",
    table_id="6hrPlevPt",
    frequency="6hrPt",
    facets=facets,
    from_timestamp=start_date.isoformat() + "Z",
    to_timestamp=end_date.isoformat() + "Z",
    latest=True,
    source_id="MIROC6",
)
search_results = ctx.search()
print(len(search_results))


# %%

cols = [
    "source_id",
    "member_id",
    "experiment_id",
    "variable_id",
    "table_id",
    "frequency",
]
df = pd.DataFrame(
    [(x[0] for x in itemgetter(*cols)(result.json)) for result in search_results],
    columns=cols,
)
df

# %%
result = search_results[0]
# opendap_urls = [file.opendap_url for file in result.file_context().search()]
files: list[pyesgf.search.results.FileResult] = result.file_context().search()

# %%
opendap_urls = []
download_urls = []
for file in files:
    regex = r".*_(\d{12})-(\d{12}).nc\|.*"
    file_stime, file_etime = pd.to_datetime(re.match(regex, file.file_id).groups())
    if max(file_stime, start_date) <= min(file_etime, end_date):
        opendap_urls.append(file.opendap_url)
        download_urls.append(file.download_url)
    # print(file_stime, file_etime, type(file_stime))
    # # print(file.json["id"])
    # # print(file.opendap_url)
print(opendap_urls)
print(download_urls)

# %%
ds = xr.open_mfdataset(opendap_urls, combine="nested", concat_dim="time")

# %%
sub_ds = ds.sel(time=slice(start_date, end_date))
util.to_netcdf(sub_ds, "test.nc")

# %%
# open the catalog
url = PANGEO_CATALOG_URL
dataframe = intake.open_esm_datastore(PANGEO_CATALOG_URL)
# dataframe.df.columns
# df = dataframe.df

# %%
sid = "EC-Earth3"
exp = "historical"
var = "ta"
table_id = "6hrPlevPt"
models = dataframe.search(
    experiment_id="ssp585",
    table_id=table_id,
    variable_id=var,
    #   source_id = sid,
    # institution_id=ins,
    # member_id=mem
)
ml = natural_sort(models.df.member_id.values)
print(models.df["source_id"].unique())
# display(models.df)
print(ml)

# %%
# get the first one only then seach again
mem = ml[0]
model_s = dataframe.search(
    experiment_id=exp,
    table_id="Amon",
    variable_id=var,
    source_id=sid,
    # institution_id=ins,
    member_id=mem,
)

# %%
ds = model_s.to_dataset_dict()
ds

# %%
dataframe.df.table_id.unique()

# %%
x = dataframe.search(table_id="3hr").df

# %%
for g in list(x.groupby("source_id"))[:]:
    print(g[0])
    y = g[1]
    print(y.variable_id.unique())

# %%
y.variable_id.unique()

# %%
x1 = dataframe.search(table_id="6hrLev").df

# %%
df.table_id.unique()

# %%
for sid in [
    "EC-Earth3",
    "MIROC6",
    "MRI-ESM2-0",
    "ACCESS-CM2",
    "IPSL-CM6A-LR",
    "MPI-ESM1-2-HR",
][:1]:
    for exp in ["historical", "ssp585", "ssp126", "ssp370", "ssp245"][:]:
        for var in ["tas", "ta", "ua", "va", "hur", "zg", "ts"][:]:
            # seach all files with information given above
            models = dataframe.search(
                experiment_id=exp,
                table_id="Amon",
                variable_id=var,
                source_id=sid,
                # institution_id=ins,
                # member_id=mem
            )
            # then one might get several files with the same conditions
            # r1: Realization (initial condition run)
            # i1: Initialization method
            # p1: Physical parameters
            # f1: External forcings

            print(var, exp, sid, len(models.df))

            # if no files exist then print out error
            if len(models.df) == 0:
                print("*** \n Erorrrr \n")

            # sort the possible files
            ml = natural_sort(models.df.member_id.values)

            # get the first one only then seach again
            mem = ml[0]
            model_s = dataframe.search(
                experiment_id=exp,
                table_id="Amon",
                variable_id=var,
                source_id=sid,
                # institution_id=ins,
                member_id=mem,
            )

            # if no files exist then print out error
            if len(model_s.df) == 0:
                print("*** \n Erorrrr \n")

            print(mem)

            if len(model_s.df) > 0:
                print("Download")

                if True:
                    try:
                        datasets = model_s.to_dataset_dict(
                            zarr_kwargs={
                                "consolidated": True,
                                "decode_times": True,
                                "use_cftime": True,
                            }
                        )
                        # datasets = models.to_dataset_dict(xarray_open_kwargs={"consolidated": True, "decode_times": True, "use_cftime": True})

                        for k, v in datasets.items():
                            odir = "Download_s8/" + sid + "/" + exp + "/"
                            if not os.path.exists(odir):
                                os.makedirs(odir)
                            ofile = odir + var + "_" + k + "_" + mem + ".nc"
                            print("write to ", ofile)
                            v.to_netcdf(ofile)
                    except:
                        print("fail")
