![Logo](docs/_static/logo.png)

***

# Project

The SIMPET project is intended to allow to setup and launch MC simulation on a simple way. It provides functionalities to: 

- Extract simple activity and attenuation maps from PET/MR images.
- Apply the BrainViset procedure to obtain realistic Activity and Attenuation maps.
- Run Analytic simulations using STIR simulation procedure and MC simulation using SimSET.

# Installtion

1. Install [Git LFS](https://git-lfs.com/).
2. Clone the repository by adding the `--recurse-submodules` flag:
```
git clone --recurse-submodules --branch develop https://github.com/txusser/simpet.git
```
3. Install [python 3.9](https://www.python.org/downloads/release/python-390/). If you use [apt](https://help.ubuntu.com/kubuntu/desktopguide/es/apt-get.html) (most Debian based distros use it):
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9
```
4. Create a python virtual environment from python 3.9, there are several options for this (we recommend [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)):
  - [venv](https://docs.python.org/es/3.9/library/venv.html).
  - [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).
  - [virtualenv](https://virtualenv.pypa.io/en/latest/).

You can isntall miniconda in Linux with the following code:
```
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```
Then restart your shell:
```
~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh
```
5. Activate the virtual environment and install the requirements with: 
```
pip install -r requirements.txt
```
Sometimes, even activating the virtual environemnt, the shell will use the wide system `pip`, you can check it with `which pip` (in Linux). In that case, you may want to locate the python interpreter of your virtual environment or an alias (most of the times `python3.9`) then run:
```
/path/to/your/virtual-environtment/bin/python3.9 -m pip install -r requirements.txt
```

6. Install the project with (we recommend to be an user with root privileges):
```
make install
```

7. Decompress dummy data with:
```
make dummy-data
```

8. Activate your virtual environment and run a test with the simulation launcher:
```
python3.9 scripts/experiment.py
```

# Usage

To make the most of this version of the project is strongly recommended to be familiar with [facebook-hydra](https://hydra.cc). The configuration of a given simulation (and reconstruction) is split into 3 groups: `global` configuration, `params`, configuration and `scanner` configuration (examples given below). The `scanner` group is a subgroup of `params` group and `params` is a subgroup of the `global` configuration.

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

# Whole Body Simulation

You can perform whole body simulations following the same logic described in the last section. You may want to add `z_min` and `z_max` parameters to the `params` configuration group. Here you can find the configuration templates:

- Example of [`global`](configs/config_test_wholebody.yaml) configuration.
- Example of [`params`](configs/params/test_wholebody.yaml) configuration group.

Then you can launch an experiment with:

```
python3.9 scripts/experiment_wholebody.py --config-name <your_config_name>
```

Even add `z_min` and `z_max` on the fly:

```
python3.9 scripts/experiment_wholebody.py --config-name <your_config_name> +params.z_min=29 +params.z_max=89
```

Or override them:

```
python3.9 scripts/experiment_wholebody.py --config-name <your_config_name> params.z_min=29 params.z_max=89
```

# BrainVISET

BrainVISET is an iterative algorithm that allows the generation of activity and attenuation maps from high-resolution CT and MRI images. To run BrainVISET you will need SPM12 and MATLAB MCR. Ensure that the configuration keys `matlab_mcr_path` (path to MATLAB MCR) and `spm_path` (path to SPM12) are well set in your `configs` file. In addition, you must also specify the names (with extension) of the CT, MRI and PET images in your `configs/params` file (keys `ct_image`, `mri_image` and `pet_image`). Then, you can run BrainVISET using the [`experiment_brainviset.py`](scripts/experiment_brainviset.py) launcher:

```
python3.9 scripts/experiment_brainviset.py --config-name <your_config_name>
```

Even change image names on the fly (or other parameters):

```
python3.9 scripts/experiment_brainviset.pyy --config-name <your_config_name> params.ct_image="my_ct.nii" params.mri_image="my_mri.nii" params.pet_image="my_pet.nii"
```

**GENERAL NOTES ON USAGE**: 

- Monte Carlo simulations usually take a lot of space. If you want to change the default Data and Results directories you can do so in the in the `global` configuration group or using [facebook-hydra](https://hydra.cc) CLI overriding syntax.
- The current version of the project can produce only sinograms and LM data using SimSET. Rest of the stuff is coming soon.
- The repository has only been tested on Ubuntu 22.04.1 LTS.

# Parameters documentation

## File under `configs` directory

### Directories

- **dir_stir**: STIR directory (you should not worry about this).
- **dir_simset**: SimSET directory (you should not worry about this).
- **matlab_mcr_path**: path to MATLAB MCR, needed for BrainVISET.
- **spm_path**: path to SPM12, needed for BrainVISET.
- **dir_data_path**: path to directory with patients or subjects.
- **dir_results_path**: path to store the results of the simulation + reconstruction.

### Interactive mode

- **interactive_mode**: if set to one you may see some prompts to prevent you to overwrite existing data

### SimSET base configuration

- **stratification**: SimSET variance technique reduction. We recommend setting it to "true"
- **forced_detection**: SimSET variance technique reduction. We recommend setting it to "true".
- **forced_non_absortion**: We recommend setting it to "true". We recommend setting it to "true".
- **acceptance_angle**: SimSET acceptance angle. We recommend setting it to 90.0 but it may need fine tunning for your case.
- **positron_range**: whether to simulate positron range or not with SimSET. We recommend setting it to "true".
- **non_colinearity**: whether to simulate non-colinearity of photons with SimSET. We recommend setting it to "true".
- **minimum_energy**: minimum energy threshold. We recommend setting it to 350.0.
- **weight_window_ratio**: we recommend setting it to 1.0.
- **point_source_voxels**: we recommend setting it to "false".
- **coherent_scatter_object**: we recommend setting it to "false".
- **coherent_scatter_detector**: we recommend setting it to "false".

See [SimSET](https://depts.washington.edu/simset/html/simset_main.html) documentation for further information.

## File under `configs/params` directory

### Simulation time and environment

- **sim_type**: one of SimSET, STIR or GATE (only SimSET working).

### Run parameters

- **do_simulation**: 1 or 0, whether to perform simulation (1) or not (0). This is useful for deactivating simulation when only reconstruction is needed. 
- **do_reconstruction**: 1 or 0, whether to perform reconstruction (1) or not (0).
- **divisions**: number os subprocesses for parallel simulation.

### PET system
- **scanner_name**: name of the PET system.
- **model_type**: we recommend setting it to "cylindrical".ç

### Input and output directories

- **patient_dirname**: name of the subdirectory in **dir_data_path** where phantoms are located.
- **output_dir**: name of the attenuation map file (with extension).

### Single simulation variables

- **act_map**: name of the subdirectory in **dir_results_path** where the results will be stored.
- **att_map**: name of the activity map file (with extension).
- **center_slice**: the slice number to be placed on the center of the scanner. If 0, automatically, the half of the slices will be calculated and used.

### Whole body simulation variables

- **z_min**: start of the acquisition, slice. 
- **z_max**: end of the acquisition, slice. We calculate the number of beds based on (z_max - z_min) and the scanner FOV.

### BrainVISET variables

- **mri_image**: MRI filename with extension.
- **ct_image**: CT filename with extension.
- **pet_image**: PET filename with extension.
- **maximumIteration**: maximum number of iterations when using BrainVISET.

### SimSET Parameters (not used by STIR sim)
- **total_dose**: dose in mCi.   
- **simulation_time**: time to be simulated in s.
- **sampling_photons**: set to 0 to avoid importance sampling. We recommend the use of importance sampling and setting this parameter to 20000000 as a starting point.
- **photons**: set to 0 to do a realistic noise simulation.
- **add_randoms**: 1 activate randoms simulation (will force sampling_photons=0 and photons=0). It can kill the process is there is not enough RAM.
- **phglistmode**: history Files from the phg module (needed for LM reconstruction, potentially very big).
- **detlistmode**: history Files from the detector module (you need this for adding randoms, if **add_randoms**=1 will be forced).                                       

## File under `configs/params/scanner` directory

### Scanner Description

- **scanner_name**: name of the scanner.                 
- **simset_material**: material of the scanner, see [SimSET](https://depts.washington.edu/simset/html/simset_main.html) for available materials.
- **average_doi**: depth of interaction.
- **scanner_radius**: radius of the scanner in cm.
- **num_rings**: number of rings of the scanner.               
- **axial_fov**: axial FOV of the scanner in cm.

### Crystal description

- **z_crystal_size**: size of the crystal in the axial direction in cm.
- **transaxial_crystal_size**: size of the cristal in the transaxial size in cm.
- **crystal_thickness**: thickness of the crystal in cm.

### Energy characteristics

- **energy_resolution**: FWHM in keV it will be divided by reference energy (511 keV).
- **min_energy_window**: min energy threshold in keV.               
- **max_energy_window**: max energy threshold in keV.   

### Sinogram creation

#### Binning

- **num_aa_bins**: number of views (half of the number of detectors per ring).
- **num_td_bins**: number of radial bins.                      

#### Coincidence window (ns)

- **coincidence_window**: used only for randoms simulation, in ns.

#### Sinogram pre-processing

- **psf_value**: sinogram preprocessing parameter.                                                              
- **add_noise**: sinogram preprocessing parameter.

### Corrections

#### Attenuation correction

- **analytical_att_correction**: performed by SimSET calcattenuation.
- **stir_recons_att_corr**:  performed in STIR by entering the att image as a normalization map.

#### Scatter Correction

- **analytic_scatt_corr_factor**: 0.15 will remove 85% of scatter, 0 will remove scatter.                                             
- **stir_scatt_corr_smoothing**: will use smoothed SimSET scatter as additive_sinogram.

#### Randoms Correction

- **analytic_randoms_corr_factor**: 0.15 will remove 85% of scatter, 0 will remove randoms.                                                 
- **stir_randoms_corr_smoothing**: will include smoothed SimSET randoms in the additive_sinogram. 

### Reconstruction

- **recons_type**: one of OSEM3D, OSEM2D, FBP2D, FBP3D.
- **max_segment**: maximum Ring difference on the reconstruction.

#### Configuration of reconstruction output

- **zoomFactor**: relation between sinogram bin size and X, Y voxel size.
- **xyOutputSize**: output matrix X,Y size in reconstruction.                                                
- **zOutputSize**: output marix Z size in reconstruction.
- **numberOfSubsets**: number of subsets in reconstruction.                                  
- **numberOfIterations**: number of iterations in iterative reconstruction.      
- **savingInterval**: interval that to save intermediate subiterations images.

#### Filter

- **inter_iteration_filter**: 1 for activation, 0 for deactivation.                                                     
- **subiteration_interval**:                                                              
- **x_dir_filter_FWHM**: postprocessing filter X size in mm.                                                                
- **y_dir_filter_FWHM**: postprocessing filter Y size in mm.                                                                 
- **z_dir_filter_FWHM**: postprocessing filter Z size in mm.                                                                                                                 

# Contributors

- Jesús Silva-Rodríguez
- Pablo Aguiar
- Aida Ninyerola-Baizan
- Jeremiah Poveda
- Francisco Javier López-González
- Nikos Efthimiou
- Arnau Farre

# References

You may find more information about STIR and SimSET parameters in their official documentation.

[1] [SimSET](https://depts.washington.edu/simset/html/simset_main.html).

[2] [STIR](https://stir.sourceforge.net/).
