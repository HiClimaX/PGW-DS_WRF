# %%
import re

import fire

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
experiment_ids = ["historical", "ssp370"]
variable_ids = ["ta", "ua", "va", "hur", "zg", "ts"]
start_date = pd.Timestamp("2010-01-01")
end_date = pd.Timestamp("2010-02-01")


# %%
def get_download_urls(
    variable_id, source_id, experiment_id, start_date, end_date, exclude_nodes: str = ""
) -> list[str]:
    exclude_nodes_set = set(exclude_nodes.split(","))

    def filter_node(results):
        return [
            result
            for result in results
            if result.json["data_node"] not in exclude_nodes_set
        ]

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    conn = SearchConnection("https://esgf.ceda.ac.uk/esg-search", distrib=True)
    facets = "project,experiment_id,variable_id,source_id,member_id,table_id,frequency,data_node"

    ctx = conn.new_context(
        project="CMIP6",
        experiment_id=experiment_id,
        variable=variable_id,
        table_id="6hrPlevPt",
        frequency="6hrPt",
        facets=facets,
        latest=True,
        source_id=source_id,
    )
    search_results = filter_node(ctx.search())
    members = util.natural_sort(
        np.unique([result.json["member_id"][0] for result in search_results])
    )

    ctx_first = ctx.constrain(member_id=members[0])
    search_results_first_member = filter_node(ctx_first.search())
    result = search_results_first_member[0]
    files: list[pyesgf.search.results.FileResult] = result.file_context().search()

    download_urls = []
    for file in files:
        regex = r".*_(\d{12})-(\d{12}).nc\|.*"
        file_stime, file_etime = pd.to_datetime(re.match(regex, file.file_id).groups())
        if max(file_stime, start_date) <= min(file_etime, end_date):
            download_urls.append(file.download_url)

    return download_urls


# %%
if __name__ == "__main__":
    fire.Fire(get_download_urls)
    exit(0)

# %%
get_download_urls("hus", "MIROC6", "ssp370", start_date, end_date)
