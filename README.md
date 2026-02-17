# PGW-DS_WRF

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

## Requirements

### OS

This program use [WRF](https://github.com/wrf-model/WRF), so we have to do in **Linux**.

### Python enviroments

We reccomend to use [anaconda](https://www.anaconda.com/) because this script need a library which can install by conda.

If you don't have anaconda, you will see [Installing Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#linux-terminal-installer)

0. Install WRF and download WPS_GEOG:

* [WRF](https://www.mmm.ucar.edu/weather-research-and-forecasting-model)
* [WPS_GEOG](https://www2.mmm.ucar.edu/wrf/users/download/get_sources_wps_geog.html)


1. It is easy if you use conda. From the base directory, which contains `environment.yml`, run

```bash
conda env create -f environment.yml
```
Details in [Requirements.md](./Requirements.md)


## Repository Structure

### Root

* [README.md](README.md) → Overview & usage
* [environment.yml](environment.yml) → Python dependencies
* [create_pgw_wps_interm.py](create_pgw_wps_interm.py) → Add PGW delta to WPS intermediate files

### Download_CMIP6/

Scripts for downloading CMIP6 GCM data:

* [download_pgw.py](Download_CMIP6/download_pgw.py) → Download CMIP6 monthly data via intake-esm
* [get_6h_url.py](Download_CMIP6/get_6h_url.py) → Get 6-hourly data URLs

### get_era5_data/

Scripts for downloading ERA5 reanalysis data:

* [GetERA5.py](get_era5_data/GetERA5.py) → Download ERA5 pressure level and single level data
* [download.sh](get_era5_data/download.sh) → Shell script for batch ERA5 download

### Run_WRF/

WRF execution and analysis notebooks:

* [Run_WRF.ipynb](Run_WRF/Run_WRF.ipynb) → Standard WRF run
* [Run_PGW.ipynb](Run_WRF/Run_PGW.ipynb) → PGW experiment run
* [PlotT2diff.ipynb](Run_WRF/PlotT2diff.ipynb) → Visualize temperature differences
* [namelist/](Run_WRF/namelist/) → WRF and WPS configuration files


## Workflow


1. **Download CMIP6 monthly data** (PGW deltas source)  
   Run `Download_CMIP6/download_pgw.py` to populate `Download_CMIP6/Download/`.
   ```bash
   cd Download_CMIP6
   python download_pgw.py
   ```

2. **Prepare reanalysis forcing (ERA5) and WPS intermediates**  
   Download ERA5 GRIBs with `get_era5_data/download.sh` (configure dates/area/output first).
   ```bash
   cd get_era5_data
   ./download.sh
   ```
   Run WPS `ungrib.exe` to produce intermediate files like `ERA5:YYYY-MM-DD_HH` (prefix comes from `namelist.wps`).
   ```bash
   ./ungrib.exe
   ```

3. **Apply PGW deltas to WPS intermediate files**  
   Run `create_pgw_wps_interm.py` to write PGW-modified intermediates to your output directory.
   ```bash
   python create_pgw_wps_interm.py
   ```

4. **Run WRF as usual**  
   Continue with `metgrid.exe`, `real.exe`, `wrf.exe`.
   ```bash
   ./metgrid.exe
   ./real.exe
   ./wrf.exe
   ```

See usage details at the top of each script: [Download_CMIP6/download_pgw.py](./Download_CMIP6/download_pgw.py), [get_era5_data/download.sh](./get_era5_data/download.sh), and [create_pgw_wps_interm.py](./create_pgw_wps_interm.py).

### Test run

We provide scripts to run PGW experiments easily in [Run_WRF/](./Run_WRF/).

- Edit `Run_WRF/namelist/namelist.wps`, `Run_WRF/namelist/namelist.input`, and `Run_WRF/namelist/GEOGRID.TBL` for your domain, timing, and physics setup.
- Run [Run_WRF.ipynb](Run_WRF/Run_WRF.ipynb) to execute the control simulation (standard WPS/WRF flow).
- Run `create_pgw_wps_interm.py` to generate PGW-modified WPS intermediate files.
  ```bash
  python create_pgw_wps_interm.py
  ```
- Run [Run_PGW.ipynb](Run_WRF/Run_PGW.ipynb) to execute the PGW-DS simulation using PGW-modified inputs.
- Compare control vs PGW-DS outputs with [PlotT2diff.ipynb](Run_WRF/PlotT2diff.ipynb) if needed.

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
