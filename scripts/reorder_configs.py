import argparse
import yaml
from typing import Dict, Mapping, Any
from pathlib import Path
from enum import Enum, auto


class SIMPETConfig(Enum):
    dir_stir = auto()
    dir_simset = auto()
    matlab_mcr_path = auto()
    spm_path = auto()
    dir_data_path = auto()
    dir_results_path = auto()
    interactive_mode = auto()
    stratification = auto()
    forced_detection = auto()
    forced_non_absortion = auto()
    acceptance_angle = auto()
    positron_range = auto()
    isotope = auto()
    non_colinearity = auto()
    minimum_energy = auto()
    weight_window_ratio = auto()
    point_source_voxels = auto()
    coherent_scatter_object = auto()
    coherent_scatter_detector = auto()


class SIMPETParams(Enum):
    sim_type = auto()
    do_simulation = auto()
    do_reconstruction = auto()
    divisions = auto()
    scanner = auto()
    model_type = auto()
    patient_dirname = auto()
    pet_image = auto()
    mri_image = auto()
    output_dir = auto()
    center_slice = auto()
    total_dose = auto()
    simulation_time = auto()
    sampling_photons = auto()
    photons = auto()
    add_randoms = auto()
    phglistmode = auto()
    detlistmode = auto()
    maximumIteration = auto()


class SIMPETScanner(Enum):
    scanner_name = auto()
    simset_material = auto()
    average_doi = auto()
    scanner_radius = auto()
    num_rings = auto()
    axial_fov = auto()
    z_crystal_size = auto()
    transaxial_crystal_size = auto()
    crystal_thickness = auto()
    energy_resolution = auto()
    num_aa_bins = auto()
    num_td_bins = auto()
    min_energy_window = auto()
    max_energy_window = auto()
    coincidence_window = auto()
    max_segment = auto()
    zoomFactor = auto()
    xyOutputSize = auto()
    zOutputSize = auto()
    zOutputVoxelSize = auto()
    numberOfSubsets = auto()
    numberOfIterations = auto()
    savingInterval = auto()
    analytical_att_correction = auto()
    stir_recons_att_corr = auto()
    analytic_scatt_corr_factor = auto()
    stir_scatt_corr_smoothing = auto()
    stir_scatt_simulation = auto()
    analytic_randoms_corr_factor = auto()
    stir_randoms_corr_smoothing = auto()
    recons_type = auto()
    inter_iteration_filter = auto()
    subiteration_interval = auto()
    x_dir_filter_FWHM = auto()
    y_dir_filter_FWHM = auto()
    z_dir_filter_FWHM = auto()
    psf_value = auto()
    add_noise = auto()


def flatten(d):
    """
    Flatten a nested ``dict``.

    Args:
        d: nested ``dict``.

    Returns:
        Flattened dict.
    """
    items = []
    for k, v in d.items():
        if isinstance(v, dict):
            items.extend(flatten(v).items())
        else:
            items.append((k, v))

    return dict(items)


def dump_config_as_ordered(config: Mapping[str, Any], order: Enum, ordered_config_path: str) -> Dict[str, Any]:
    """
    Dump a config as a YAML file with
    the order specified by the input ``Enum``

    Args:
        config: ``dict``-like config.
        order: ``Enum`` specifiying the order.
        ordered_config_path: full filepath fot storing the ordered config.

    Returns:
        The ordered config as ``dict``.
    """
    ordered_config_path = Path(ordered_config_path)

    with open(config_path, 'r') as cfg:
        config = flatten(yaml.safe_load(cfg))

    ordered_keys = [param.name for param in order]

    ordered_cfg = []
    for key in ordered_keys:
        value = config.get(key)
        if value:
            ordered_cfg.append((key, value))

    ordered_cfg = dict(ordered_cfg)
    with open(ordered_config_path, 'w') as rcfg:
        yaml.dump(dict(ordered_cfg), rcfg, sort_keys=False)

    return ordered_cfg


parser = argparse.ArgumentParser(description='Reorder SIMPET hydra-based configurations.')
parser.add_argument("config", type=Path)
args = vars(parser.parse_args())
config_path = args["config"].resolve()


with open(config_path, 'r') as cfg:
    config = flatten(yaml.safe_load(cfg))

dump_config_as_ordered_kwargs = [
    {
        "config": config,
        "order": SIMPETConfig,
        "ordered_config_path": config_path.with_name("config_ordered.yaml")
    },
    {
        "config": config,
        "order": SIMPETParams,
        "ordered_config_path": config_path.with_name("params_ordered.yaml")
    },
    {
        "config": config,
        "order": SIMPETScanner,
        "ordered_config_path": config_path.with_name("scanner_ordered.yaml")
    }
]
config_names = ["config", "params", "scanner"]

config = {}
for name, kw in zip(config_names, dump_config_as_ordered_kwargs):
    config[name] = dump_config_as_ordered(**kw)

reordered_config = {}
reordered_config = config["config"]
reordered_config["params"] = config["params"]
reordered_config["params"]["scanner"] = config["scanner"]

with open(config_path.with_name("single_config_ordered.yaml"), 'w') as ocfg:
    yaml.dump(reordered_config, ocfg, sort_keys=False)
