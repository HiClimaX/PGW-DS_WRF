# Requirements

- **OS**

This program use [WRF](https://github.com/wrf-model/WRF), so we have to do in **Linux**.

- **Python environments**

We recommend to use [anaconda](https://www.anaconda.com/) because this script need a library which can install by conda.

If you don't have anaconda, you will see [Installing Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#linux-terminal-installer)

if you finish installing anaconda, you should create environment with Python3.10 - 3.12.

```bash
conda create -n pgw-ds python=3.12
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

This scripts use [jupyternotebook](https://jupyter-notebook.readthedocs.io/en/latest/) (".ipynb" file), so you will use [jupyter lab](https://jupyter.org/install) (jupyter hub) or [VS code extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter).

If you want to use **JupyterLab**, just follow the steps.

```bash
pip install jupyterlab
```
or 
```bash
conda install jupyterlab
```

If you already use Jupyter, you can make the environment (**pgw-ds**) available by installing `ipykernel`.

```bash
conda install ipykernel
```

If the kernel is not recognized.

```bash
python -m ipykernel install --user --name=pgw-ds --display-name "Python (PGW-DS)"
```


