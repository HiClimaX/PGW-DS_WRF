# PGW-DS\_WRF

**Pseudo-Global-Warming (PGW) downscaling using WRF**

This repository provides scripts, datasets, and workflows for conducting **Pseudo-Global Warming (PGW)** downscaling experiments with the **Weather Research and Forecasting (WRF)** model. It is designed to be modular, reproducible, and extendable for different regions and scenarios.

## Authors

* **Quang-Van Doan** – University of Tsukuba 
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

* `README.md` → Overview & usage
* `requirements.txt` → Python dependencies
* `docs/` → Documentation
* `data/` → Input and processed datasets
* `scripts/` → Preprocessing, PGW, WRF, postprocessing
* `outputs/` → Simulation results and figures
* `tests/` → Unit tests

### docs/

* `guideline.md`
* `data_sources.md`

### data/

* `raw/` → Raw input datasets
* `processed/` → Processed forcing fields
* `sample/` → Small test datasets

### scripts/

* `preprocess/` → Preprocessing scripts
* `pgw/` → PGW anomaly scripts
* `downscaling/` → WRF setup and run scripts
* `postprocess/` → Extraction & visualization scripts

### outputs/

* `wrf/` → WRF simulation outputs
* `figures/` → Plots and maps
* `standardized/` → CMORized outputs

### tests/

* Unit tests for reproducibility


## Installation

1. Clone the repository:

```bash
git clone https://github.com/HiClimaX/PGW-DS_WRF.git
cd PGW-DS_WRF
```

2. Create and activate environment:

```bash
conda create -n pgw python=3.10
conda activate pgw
pip install -r requirements.txt
```

3. Install WRF:

* [WRF](https://www.mmm.ucar.edu/weather-research-and-forecasting-model)


## Data

Required datasets:

* **Reanalysis**: ERA5 (ECMWF) or JRA-55
* **GCM Data**: CMIP6 (historical and scenario experiments)
* **Sample Data**: Provided in `data/sample/`

Expected folder structure:

```
data/
  ├── raw/
  │   ├── ERA5/
  │   └── CMIP6/
  ├── processed/
  └── sample/
```


## Workflow

1. **Preprocessing**

```bash
python scripts/preprocess/extract_forcing.py
python scripts/preprocess/apply_bias_correction.py
```

2. **Compute PGW anomalies**

```bash
python scripts/pgw/compute_anomalies.py
python scripts/pgw/apply_pgw.py
```

3. **Run WRF with PGW forcing**

```bash
bash scripts/downscaling/run_wrf.sh
```

4. **Post-processing & visualization**

```bash
python scripts/postprocess/extract_timeseries.py
python scripts/postprocess/plot_maps.py
python scripts/postprocess/cmorize_output.py
```

## 📈 Example Output

* WRF simulation: `outputs/wrf/sample_output.nc`
* Visualization: `outputs/figures/temperature_anomaly.png`
* Standardized output: `outputs/standardized/pgw_output_CMOR.nc`

---



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
