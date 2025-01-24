#!/bin/bash

# Sometimes some nodes are not working, so we can exclude them
exclude_nodes=esgf-data1.llnl.gov,esgf.ceda.ac.uk

options=(--exclude_nodes "$exclude_nodes")

parallel python download_6h.py "${options[@]}" ::: ta ua va hus zg ts ::: MIROC6 ::: historical ::: "2010-01-01" ::: "2010-02-01" | tee ./Download_6hr/urls.txt
parallel python download_6h.py "${options[@]}" ::: ta ua va hus zg ts ::: MIROC6 ::: ssp370 ::: "2050-01-01" ::: "2050-02-01" | tee -a ./Download_6hr/urls.txt
