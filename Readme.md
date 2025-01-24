# Pseudo-global-warming downscaling (PGW-DS) program

We tested these scripts on Python 3.12.

## Install libraries

It is easy if you use conda. From the base directory, which contains `environment.yml`, run

```bash
conda env install
```

## Download CMIP6 GCM monthly data

```bash
cd Download_CMIP6
python download_cmip6.py
```

## Create WPS intermediate files

We have tested for ERA5 pressure levels data.

The steps are:

1. Download ERA5 data.
```bash
cd get_era5_data
./download.sh
```
Modify the script accordingly for your region of interest.

2. Use WPS to ungrib the grib file. You should get a bunch of files with names
similar to `FILE:2000-01-10_19` or `ERA5:2000-01-10_19`. The prefix (`FILE` or
`ERA5`) can be set in the `namelist.wps` file. We use the ERA5 prefix.

3. Run the script to add PGW delta to variables in WPS intermediate files.
```bash
python create_pgw_wps_interm.py
```

4. Run other WRF steps (e.g., `metgrid.exe`) as usual.

## Test run with WRF

In Run_WRF/

Run_WRF/Run_WRF.ipynb

Run_WRF/Run_PGW.ipynb

## Relevant data are saved to:

https://drive.google.com/drive/folders/1-DgBXOMXOd7CokSxHDvA2XrcZtOSoWfj?usp=drive_link
