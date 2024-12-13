#!/bin/bash

parallel python download_6h.py ::: ta ua va hur zg ts ::: MIROC6 ::: historical ::: "2010-01-01" ::: "2010-02-01" | tee ./Download_6hr/urls.txt
parallel python download_6h.py ::: ta ua va hur zg ts ::: MIROC6 ::: ssp370 ::: "2050-01-01" ::: "2050-02-01" | tee -a ./Download_6hr/urls.txt
