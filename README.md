# PGW-DS_WRF

This repository provides scripts, datasets, and workflows for conducting Pseudo-Global Warming (PGW) downscaling experiments using the WRF model.
It is designed for reproducibility, transparency, and easy adaptation to new regions or datasets.

## 👥 Authors

- Quang-Van Doan (University of Tsukuba, Japan) – Lead developer
- Mamoru Yuasa (University of Tsukuba, Japan) 
- [Your collaborators here]
- 

## Overview

Pseudo-Global Warming (PGW) is a widely used approach to assess the influence of climate change on high-resolution weather and climate simulations.
It works by applying large-scale climate change anomalies from GCMs to reanalysis data, then using the modified forcing to drive regional climate models such as WRF.

This repository includes:

> Scripts to preprocess reanalysis and GCM data.

> Tools to compute and apply PGW anomalies.

> WRF configuration templates for downscaling.

> Post-processing and visualization tools.

> Sample input/output files for testing.

## Repository Structure

PGW-Downscaling/
├── README.md               # Overview & usage
├── requirements.txt        # Python dependencies
├── docs/                   # Documentation
├── data/                   # Input & sample datasets
├── scripts/                # Preprocess, PGW, downscaling, postprocess
├── outputs/                # Example outputs & visualizations
└── tests/                  # Unit tests for reproducibility

## Installation

Clone the repository:

git clone https://github.com/your-org/PGW-Downscaling.git
cd PGW-Downscaling


Create environment:

conda create -n pgw python=3.10
conda activate pgw
pip install -r requirements.txt


Install WRF, CDO, and NCO for downscaling and data manipulation.

## Data

The following datasets are required:

Reanalysis: ERA5, JRA-55, or equivalent.

GCM Data: CMIP6 historical + future scenario runs.

Sample Data: Provided in data/sample/ for testing.

Data must be stored under:

data/raw/
   ├── ERA5/
   ├── CMIP6/
   └── sample/

## Workflow

### Preprocessing

Extract and regrid ERA5 / CMIP6 data.

Apply bias correction if necessary.

python scripts/preprocess/extract_forcing.py


### Compute PGW Anomalies

Calculate monthly mean anomalies (future – historical).

Apply anomalies to reanalysis baseline.

python scripts/pgw/compute_anomalies.py
python scripts/pgw/apply_pgw.py


### Downscaling (WRF)

Configure namelist.input (template provided).

Run WRF with PGW-modified inputs.

bash scripts/downscaling/run_wrf.sh


### Post-Processing

Extract timeseries, generate maps, CMORize outputs.

python scripts/postprocess/plot_maps.py


### Example Output

WRF simulation: outputs/wrf/sample_output.nc

Visualization: outputs/figures/temperature_anomaly.png

Standardized output: outputs/standardized/pgw_output_CMOR.nc

## References

Schär, C., et al. (1996). The Pseudo-Global Warming Method: A Tool to Investigate Climate Change Impacts.

Rasmussen, R., et al. (2011). Simulation of extreme precipitation events using PGW approach.

Doan Q.V. and Kusaka H. (2018)

📜 License

This repository is licensed under the MIT License.
