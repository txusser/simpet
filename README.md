
![Logo](docs/_static/logo.png)

***

# Project

The SIMPET project is intended to allow to setup and launch MC simulation on a simple way. It provides functionalities to: 

- Extract simple activity and attenuation maps from PET/MR images.
- Apply the BrainViset procedure to obtain realistic Activity and Attenuation maps.
- Run Analytic simulations using STIR simulation procedure and MC simulation using SimSET.

# Installtion

- Install [Git LFS](https://git-lfs.com/).
- Install [python 3.9](https://www.python.org/downloads/release/python-390/).
- Create a python virtual environment from python 3.9, there are several options for this (we recommend [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)):
  - [venv](https://docs.python.org/es/3.9/library/venv.html).
  - [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).
  - [virtualenv](https://virtualenv.pypa.io/en/latest/).
- Activate the virtual environment and install the requirement with `pip install -r requirements.txt`.
- Run `make install`.
- Run a test with `python3.9 scripts/experiment.py` or `python scripts/experiment.py` (make sure that you are using the interpreter of the virtual environment created in the previous step).

# Usage

In order to make the most of this version of the project is strongly recommended to be familiar with [facebook-hydra](https://hydra.cc). The configuration of a given simulation (and reconstruction) is split into 3 groups: `global` configuration, `params`, configuration and `scanner` configuration (examples given below). The `scanner` group is a subgroup of `params` group and `params` is a subgroup of the `global` configuration.

- Example of [`global`](configs/config_test.yaml) configuration.
- Example of [`params`](configs/params/test.yaml) configuration group.
- Example of [`scanner`](configs/params/scanner/discovery_st.yaml) configuration group.

This approach allows the user to have several configuration groups and switch between them at no cost. For example, given the following tree of configurations (each subgroup has a "production" configuration and a "test" configuration):

```
.
└── configs/
    ├── config_prod.yaml  # global configuration group
    ├── config_test.yaml  # global configuration group
    └── params/
        ├── params_prod.yaml
        ├── params_test.yaml
        └── scanner/
            ├── siemens.yaml
            └── discovery.yaml
```

Using [facebook-hydra](https://hydra.cc) override syntax, switching between configurations is trivial:

```
# Running test configuration with Siemens scanner
python scripts/experiment.py --config-name config_test params/scanner=siemens
```

```
# Running prod configuration with test `params` and Discovery scanner
python scripts/experiment.py --config-name config_prod params=params_test params/scanner=discovery
```

```
# Running prod configuration with test `params` and Discovery scanner but doing only reconstruction
python scripts/experiment.py --config-name config_prod params=params_test params/scanner=discovery params.do_simulation=0
```

```
# Running prod configuration with test `params` and Discovery scanner, doing only reconstruction and overriding the scanner radius
python scripts/experiment.py --config-name config_prod params=params_test params/scanner=discovery params.do_simulation=0 params.scanner.scanner_radius=35
```

**NOTES ON USAGE**: 

- Monte Carlo simulations usually take a lot of space. If you want to change the default Data and Results directories you can do so in the in the `global` configuration group or using [facebook-hydra](https://hydra.cc) CLI overriding syntax.
- The current version of the project is able to produce only sinograms and LM data using SimSET. Rest of the stuff is coming soon.
- The repository has only been tested on Ubuntu 22.04.1 LTS.
- It is possible to use [Weights & Biases](https://wandb.ai/site) (W&B) to log slices (sinograms, activity maps, etc.) and main logs. Using this option requires the creation of a project and additional steps described in the W&B official documentation. You can disable this option by setting `log=false`.
- You may want to use `git update-index --assume-unchanged <full-path-configs>` in order to ignore your user-defined configurations or to not commit changes to the default test configuration (actually, there is a git filter to reset the remote test configuration in each push).

# Contributors

- Jesús Silva-Rodríguez
- Pablo Aguiar
- Aida Ninyerola-Baizan
- Jeremiah Póveda
- Francisco Javier López-González
- Nikos Efthimiou
- Arnau Farre

