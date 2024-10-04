# %%
import re
from pathlib import Path

# from operator import itemgetter
import numpy as np
import pandas as pd
import pyesgf.search
import util
from pyesgf.search import SearchConnection

# %%
source_ids = [
    "EC-Earth3",
    "MIROC6",
    "MRI-ESM2-0",
    "ACCESS-CM2",
    "IPSL-CM6A-LR",
    "MPI-ESM1-2-HR",
]
experiment_ids = ["historical", "ssp585", "ssp126", "ssp370", "ssp245"]
variable_ids = ["tas", "ta", "ua", "va", "hur", "zg", "ts"]
start_date = pd.Timestamp("2010-01-01")
end_date = pd.Timestamp("2010-02-01")

# %%
conn = SearchConnection("https://esgf.ceda.ac.uk/esg-search", distrib=True)
facets = "project,experiment_id,variable_id,source_id,member_id,table_id,frequency"

# %%
ctx = conn.new_context(
    project="CMIP6",
    experiment_id="historical",
    variable="ta",
    table_id="6hrPlevPt",
    frequency="6hrPt",
    facets=facets,
    latest=True,
    source_id="MIROC6",
)
search_results = ctx.search()
print(len(search_results))

# %%
members = util.natural_sort(
    np.unique([result.json["member_id"][0] for result in search_results])
)
members

# %%
ctx_first = ctx.constrain(member_id=members[0])
search_results_first_member = ctx_first.search()
# There can be several results from several replica
print(f"Found {len(search_results_first_member)} replicas")

# %%

# cols = [
#     "source_id",
#     "member_id",
#     "experiment_id",
#     "variable_id",
#     "table_id",
#     "frequency",
# ]
# df = pd.DataFrame(
#     [(x[0] for x in itemgetter(*cols)(result.json)) for result in search_results_first_member[0]],
#     columns=cols,
# ).sort_values("member_id")
# df

# %%
result = search_results_first_member[0]
files: list[pyesgf.search.results.FileResult] = result.file_context().search()

# %%
# opendap_urls = []
download_urls = []
for file in files:
    regex = r".*_(\d{12})-(\d{12}).nc\|.*"
    file_stime, file_etime = pd.to_datetime(re.match(regex, file.file_id).groups())
    if max(file_stime, start_date) <= min(file_etime, end_date):
        # opendap_urls.append(file.opendap_url)
        download_urls.append(file.download_url)
    # print(file_stime, file_etime, type(file_stime))
    # # print(file.json["id"])
    # # print(file.opendap_url)
# print(opendap_urls)
print(download_urls)

# %%
output_dir = Path("Download_6hr")
output_dir.mkdir(exist_ok=True)

with open(output_dir / "urls.txt", "w") as f:
    for url in download_urls:
        f.write(url + "\n")
