#!/bin/bash

set -eou pipefail

# Usage:
#   cd get_era5_data
#   ./download.sh
#
# Configure:
#   - DATADIR, DATE1, DATE2
#   - North, West, South, East (area bounds)
#
# Output:
#   $DATADIR/<YYYY>/ERA5-<YYYYMMDD>-<sl|pl>.grib

# Please set the following variables:
# Japan
DATADIR="$REANAL/era5/japan/"
DATE1=20110801
DATE2=20110831
North=55
West=110
South=20
East=155

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

parallel -j 2 --bar --plus \
    python GetERA5.py '{1}' '{2}' --area "$North,$West,$South,$East" --output-file "$DATADIR/{2:0:4}/ERA5-{2}-{1}.grib" \
    ::: sl pl ::: "${dates[@]}"
