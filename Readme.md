# Pseudo-global-warming downscaling (PGW-DS) program

## Requirements

- **OS**

This program use [WRF](https://github.com/wrf-model/WRF), so we have to do in **Linux**.

- **Python enviroments**

We reccomend to use [anaconda](https://www.anaconda.com/) because this script need a library which can install by conda.

If you don't have anaconda, you will see [Installing Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#linux-terminal-installer)

if you finish installing anaconda, you should create enviroment with Python3.10 - 3.12.

```bash
conda create -n pgw-ds Python=3.12
```
```bash
conda activate pgw-ds
```

You should install [gcsfs](https://gcsfs.readthedocs.io/en/latest/), [intake-esm](https://intake-esm.readthedocs.io/en/stable/), [xesmf](https://xesmf.readthedocs.io/en/latest/index.html), [wrf-python](https://wrf-python.readthedocs.io/en/latest/), [cartopy](https://scitools.org.uk/cartopy/docs/latest/), [pywinter](https://pywinter.readthedocs.io/en/latest/)

```bash
conda install -c conda-forge gcsfs intake-esm xesmf wrf-python cartopy
```

```bash
pip install git+https://github.com/dniloash/Pywinter
```

- **Jupyter setup**

This scripts use jupyternotebook (".ipynb" file), so you will use jupyter lab (jupyter hub) or VS code.

If you already can use jupyter, you can use the enviroment as follow.

```bash
conda install ipykernel
```

If the kernel is not recognized.

```bash
python -m ipykernel install --user --name=pgw-ds --display-name "Python (PGW-DS)"
```







## Download CMIP6 GCM monthly data
Script is in Download_CMIP6/

Download_CMIP6/download_pgw.ipynb

## Create Global Warming Increment (GWI) file

01_Create_GWI_files.ipynb

## Create WRF intermediate files from GWI and reanalysis data 

02_Create_PGW_WRFinterp.ipynb

## Test run with WRF

In Run_WRF/

Run_WRF/Run_WRF.ipynb

Run_WRF/Run_PGW.ipynb

## Relevant data are saved to:

https://drive.google.com/drive/folders/1-DgBXOMXOd7CokSxHDvA2XrcZtOSoWfj?usp=drive_link


