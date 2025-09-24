#!/bin/bash

set -eou pipefail

DATADIR=data/

# DATE1=20170419
# DATE2=20170419
# Nort=60
# West=80
# Sout=15
# East=150

# Japan
DATADIR=data/japan/
DATE1=20231231
DATE2=20241231
Nort=50
West=125
Sout=25
East=150

# Generate list of dates
dates=()

# Loop from DATE1 to DATE2
date=$DATE1
while [[ $date -le $DATE2 ]]; do
    dates+=("$date")
    mkdir -p "$DATADIR/$(date -d "$date" +%Y)"
    date=$(date -d "$date +1day" +%Y%m%d)
done

echo "Dates:" "${dates[@]}"

parallel -j 2 --bar --joblog download.log --resume-failed --plus \
    python GetERA5.py '{1}' '{2}' --area "$Nort,$West,$Sout,$East" --output-file "$DATADIR/{2:0:4}/ERA5-{2}-{1}.grib" \
    ::: sl pl ::: "${dates[@]}"
