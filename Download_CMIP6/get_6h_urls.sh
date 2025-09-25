#!/bin/bash

# Sometimes some nodes are not working, so we can exclude them
exclude_nodes=esgf-data1.llnl.gov,esgf.ceda.ac.uk
exclude_nodes="none"

options=(--exclude_nodes "$exclude_nodes")

# parallel python download_6h.py "${options[@]}" ::: ta ua va hus zg ::: MIROC6 ::: ssp370 ::: "2050-01-02" ::: "2050-01-30" ::: 6hrPlevPt | tee -a ./Download_6hr/urls.txt

tail -n +2 model_conf/MIROC6.csv |
    parallel --lb --colsep=, python download_6h.py \
        "${options[@]}" '{1}' '{2}' '{3}' MIROC6 historical "2010-01-02" "2010-01-30" |
    tee ./Download_6hr/urls.txt

tail -n +2 model_conf/MIROC6.csv |
    parallel --lb --colsep=, python download_6h.py \
        "${options[@]}" '{1}' '{2}' '{3}' MIROC6 ssp370 "2050-01-02" "2050-01-30" |
    tee -a ./Download_6hr/urls.txt
