![Logo](docs/_static/logo.png)

***

# Project

The SIMPET project is intended to allow to setup and launch MC simulation on a simple way. It provides functionalities to: 

- Extract simple activity and attenuation maps from PET/MR images.
- Apply the BrainViset procedure to obtain realistic Activity and Attenuation maps.
- Run Analytic simulations using STIR simulation procedure and MC simulation using SimSET.

**NOTES ON USAGE**: 

- The current version of the project is able to produce only sinograms and LM data using SimSET. Rest of the stuff is coming soon.
- The repository has only been tested on Ubuntu 22.04.1 LTS.

# Installtion

- Install [Git LFS](https://git-lfs.com/).
- Install [python 3.9](https://www.python.org/downloads/release/python-390/).
- Create a python virtual environment from python 3.9, there are several options for this (we recommend [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)):
  - [venv](https://docs.python.org/es/3.9/library/venv.html).
  - [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).
  - [virtualenv](https://virtualenv.pypa.io/en/latest/).
- Activate the virtual environment and install the requirement with `pip install -r requirements.txt`.
- Run `make install`.
- Run a test with `python3.9 test.py` or `python test.py` (make sure that you are using the interpreter of the virtual environment created in the previous step).

***

Developed by: Jesús Silva-Rodríguez.

