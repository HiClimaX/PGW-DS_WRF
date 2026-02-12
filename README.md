# PGW-DS\_WRF

**Pseudo-Global-Warming (PGW) downscaling using WRF**

This repository provides scripts, datasets, and workflows for conducting **Pseudo-Global Warming (PGW)** downscaling experiments with the **Weather Research and Forecasting (WRF)** model. It is designed to be modular, reproducible, and extendable for different regions and scenarios.

## Authors

* **Quang-Van Doan** – University of Tsukuba 
* **Do Ngoc Khanh** – Shibaura Institute of Technology 
* **Mamoru Yuasa** – University of Tsukuba


## Overview

Pseudo-Global Warming (PGW) experiments are widely used to evaluate the impact of climate change on high-resolution weather and climate simulations. The PGW approach modifies reanalysis datasets with large-scale climate anomalies derived from GCMs (e.g., CMIP6), then uses the adjusted fields as forcing for WRF.

This repository includes:

* Preprocessing tools for reanalysis and GCM data.
* Scripts for PGW anomaly calculation and application.
* WRF configuration templates.
* Post-processing and visualization scripts.
* Sample datasets and outputs for testing.


## Repository Structure

### Root

* [README.md](README.md) → Overview & usage
* [environment.yml](environment.yml) → Python dependencies
* [create_pgw_wps_interm.py](create_pgw_wps_interm.py) → Add PGW delta to WPS intermediate files

### [Download_CMIP6/](Download_CMIP6/)

Scripts for downloading CMIP6 GCM data:

* [download_pgw.py](Download_CMIP6/download_pgw.py) → Download CMIP6 monthly data via intake-esm
* [get_6h_url.py](Download_CMIP6/get_6h_url.py) → Get 6-hourly data URLs

### [get_era5_data/](get_era5_data/)

Scripts for downloading ERA5 reanalysis data:

* [GetERA5.py](get_era5_data/GetERA5.py) → Download ERA5 pressure level and single level data
* [download.sh](get_era5_data/download.sh) → Shell script for batch ERA5 download

### [Run_WRF/](Run_WRF/)

WRF execution and analysis notebooks:

* [Run_WRF.ipynb](Run_WRF/Run_WRF.ipynb) → Standard WRF run
* [Run_PGW.ipynb](Run_WRF/Run_PGW.ipynb) → PGW experiment run
* [PlotT2diff.ipynb](Run_WRF/PlotT2diff.ipynb) → Visualize temperature differences
* [namelist/](Run_WRF/namelist/) → WRF and WPS configuration files


## Requirements

0. Install WRF and download WPS_GEOG:

* [WRF](https://www.mmm.ucar.edu/weather-research-and-forecasting-model)
* [WPS_GEOG](https://www2.mmm.ucar.edu/wrf/users/download/get_sources_wps_geog.html)

1. It is easy if you use conda. From the base directory, which contains `environment.yml`, run

```bash
conda env create -f environment.yml
```


## Workflow

### 1. Download CMIP6 GCM monthly data

See [Download_CMIP6/download_pgw.py](Download_CMIP6/download_pgw.py)

```bash
cd Download_CMIP6
python download_pgw.py
```

### 2. Create WPS intermediate files

We have tested for ERA5 pressure levels data.

The steps are:

1. Download ERA5 data. See [get_era5_data/GetERA5.py](get_era5_data/GetERA5.py)
```bash
cd get_era5_data
./download.sh
```
Modify the script accordingly for your region of interest.

2. Use WPS to ungrib the grib file. You should get a bunch of files with names
similar to `FILE:2000-01-10_19` or `ERA5:2000-01-10_19`. The prefix (`FILE` or
`ERA5`) can be set in the [namelist.wps](Run_WRF/namelist/namelist.wps) file. We use the ERA5 prefix.

3. Run the script to add PGW delta to variables in WPS intermediate files. See [create_pgw_wps_interm.py](create_pgw_wps_interm.py)
```bash
python create_pgw_wps_interm.py
```

### 3. Run other WRF steps (e.g., `metgrid.exe`) as usual.

 **Test run with WRF**

In [Run_WRF/](Run_WRF/)

* [Run_WRF.ipynb](Run_WRF/Run_WRF.ipynb)
* [Run_PGW.ipynb](Run_WRF/Run_PGW.ipynb)

---

## Data

Required datasets:

* **Reanalysis**: ERA5 (ECMWF)
* **GCM Data**: CMIP6 (historical and scenario experiments)

Expected folder structure:

```
Download_CMIP6/
  └── Download/
      ├── EC-Earth3/
      │   ├── historical/
      │   └── ssp585/
      ├── MIROC6/
      │   ├── historical/
      │   └── ssp585/
      ├── MRI-ESM2-0/
      ├── ACCESS-CM2/
      ├── IPSL-CM6A-LR/
      └── MPI-ESM1-2-HR/
ERA5/
  └── (ERA5 GRIB files)
```


## Citation

If you use this repository, please cite:

```
Doan, Q.-V., et al. (2025). PGW-DS_WRF: Pseudo-global-warming downscaling using WRF. GitHub Repository. https://github.com/HiClimaX/PGW-DS_WRF
```

---

## References

* Schär, C., et al. (1996). *The Pseudo-Global Warming Method: A Tool to Investigate Climate Change Impacts*.
* Rasmussen, R., et al. (2011). *Simulation of extreme precipitation events using PGW approach*.
* Doan, Q.V. and Kusaka, H. (2018). **.



## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
