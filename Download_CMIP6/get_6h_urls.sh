#!/bin/bash

set -eou pipefail

# Sometimes some nodes are not working, so we can exclude them
exclude_nodes=()
# Example
# exclude_nodes+=(esgf-node.llnl.gov)
# exclude_nodes+=(esgf.ceda.ac.uk)
exclude_nodes+=(esgf-data02.diasjp.net)

options=()

if [ ${#exclude_nodes[@]} -gt 0 ]; then
	options+=(--exclude_nodes "${exclude_nodes[@]}")
fi

awk -F, '(NR > 1) && $2' model_conf/MIROC6.csv |
	parallel -j 4 --delay 3 --lb --colsep=, python get_6h_url.py \
		"${options[@]}" --variable_id '{1}' --table_id '{2}' --frequency '{3}' \
		--source_id MIROC6 --experiment_id historical --start_date "2010-01-02" --end_date "2010-01-30" |
	tee ./Download_6h/urls.txt

awk -F, '(NR > 1) && $2' model_conf/MIROC6.csv |
	parallel -j 4 --delay 3 --lb --colsep=, python get_6h_url.py \
		"${options[@]}" --variable_id '{1}' --table_id '{2}' --frequency '{3}' \
		--source_id MIROC6 --experiment_id ssp370 --start_date "2050-01-02" --end_date "2050-01-30" |
	tee -a ./Download_6h/urls.txt
