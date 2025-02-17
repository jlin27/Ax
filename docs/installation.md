---
id: installation
title: Installation
---

## Requirements
You need Python 3.6 or later to run Ax.

The required Python dependencies are:

* [botorch](https://www.botorch.org)
* jinja2
* pandas
* scipy
* sklearn
* plotly >=2.2.1

## Stable Version

### Installing via pip
We recommend installing Ax via pip (even if using Conda environment):

```
conda install pytorch torchvision -c pytorch  # OSX only (details below)
pip3 install ax-platform
```

Installation will use Python wheels from PyPI, available for [OSX, Linux, and Windows](https://pypi.org/project/ax-platform/#files).

*Recommendation for MacOS users*: PyTorch is a required dependency of BoTorch, and can be automatically installed via pip.
However, **we recommend you [install PyTorch manually](https://pytorch.org/get-started/locally/#anaconda-1) before installing Ax, using the Anaconda package manager**.
Installing from Anaconda will link against MKL (a library that optimizes mathematical computation for Intel processors).
This will result in up to an order-of-magnitude speed-up for Bayesian optimization, as at the moment, installing PyTorch from pip does not link against MKL.

If you need CUDA on MacOS, you will need to build PyTorch from source. Please consult the PyTorch installation instructions above.

### Optional Dependencies

To use Ax with a notebook environment, you will need Jupyter. Install it first:
```
pip3 install jupyter
```

If you want to store the experiments in MySQL, you will need SQLAlchemy:
```
pip3 install SQLAlchemy
```

## Latest Version

### Installing from Git

You can install the latest (bleeding edge) version from Git:

```
pip3 install cython numpy  # needed for compiling Cython code
pip3 install git+ssh://git@github.com/facebook/Ax.git#egg=Ax
```

See recommendation for installing PyTorch for MacOS users above.

At times, the bleeding edge for Ax can depend on bleeding edge versions of BoTorch (or GPyTorch). We therefore recommend installing those from Git as well:
```
pip3 install git+https://github.com/cornellius-gp/gpytorch.git
pip3 install git+https://github.com/pytorch/botorch.git
```

### Optional Dependencies

If using Ax in Jupyter notebooks:

```
pip3 install git+ssh://git@github.com/facebook/Ax.git#egg=Ax[notebook]
```

If storing Ax experiments via SQLAlchemy in MySQL or SQLite:
```
pip3 install git+ssh://git@github.com/facebook/Ax.git#egg=Ax[mysql]
```

## Development

When contributing to Ax, we recommend cloning the [repository](https://github.com/facebook/Ax) and installing all optional dependencies:

```
# bleeding edge versions of GPyTorch + BoTorch are recommended
pip3 install git+https://github.com/cornellius-gp/gpytorch.git
pip3 install git+https://github.com/pytorch/botorch.git

pip3 install cython numpy  # needed for compiling Cython code
git clone https://github.com/facebook/ax.git
cd ax
pip3 install -e .[notebook,mysql,dev]
```

See recommendation for installing PyTorch for MacOS users above.
