#!/bin/bash

python to_wps_interm.py \
	--model_conf_path model_conf/MIROC6.csv \
	--start_date 2050-01-05 \
	--end_date 2050-01-12 \
	--interval 6h \
	--prefix wps_interm/MIROC6_SSP370 \
	--nc_files Download_6h/*MIROC6_ssp370*.nc
