import sys
import hydra
import wandb
import shutil
import yaml
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from collections import OrderedDict
from typing import List, Union, Mapping, Any
from enum import Enum
from pathlib import Path
from pyprojroot import here
from omegaconf import DictConfig, OmegaConf

sys.path.append(str(here()))
import simpet


SAVE_IMAGE_PATH = here().parent.joinpath("Experiments")
SAVE_IMAGE_PATH.mkdir(parents=True, exist_ok=True)


class ImageExtension(Enum):
    """
    Image files extensions.
    """
    NIFTI = '.nii'
    NIFTI_GZ = '.nii.gz'
    ANALYZE = '.img'


class LogFileExtension(Enum):
    """
    Log files extensions.
    """
    LOG = '.log'
    TXT = '.txt'


class BeginWithVariableFileNames(Enum):
    rec_OSEM = "recon.img"
    rec_FBP3D = "recon.img"


class EndsWithVariableFilenames(Enum):
    Act_Map_NIfTI = "actMap.nii"
    Act_Map_Analyze = "actMap.img"
    Att_Map_NIfTI = "attMap.nii"
    Att_Map_Analyze = "attMap.img"


def remove_dir_contents(dirpath: Union[str, Path]) -> None:
    """
    Remove the contents of a dir but not the dir itself.

    Args:
        dirpath: path to the dir.
    """
    results_dir = Path(dirpath)
    for content in results_dir.iterdir():
        if content.is_file():
            content.unlink()
        elif content.is_dir():
            shutil.rmtree(content)


def get_central_slices(path: Union[str, Path]) -> OrderedDict[str, np.ndarray]:
    """
    Find all images in a given path recursively (according to
    :py:class:`ImageExtension`) and return the central
    slices in a ``dict``.

    Args:
        path: path to a directory having images (the
        the images are searched recursively).

    Returns:
        ``dict`` with filenames as keys
        and central slices as values.
    """
    path_ = Path(path)

    image_extensions = [ext.value for ext  in ImageExtension]
    image_files = [(file_.name, file_) for file_ in path_.rglob("**/*") if "".join(file_.suffixes) in image_extensions]
    images = [(filename, nib.load(img_file).get_fdata()) for filename, img_file in image_files]

    images_with_corrected_names = []
    for filename, img in images:
        name_img = (filename, img)

        for variable_name in BeginWithVariableFileNames:
            if filename.startswith(variable_name.name):
                name_img = (variable_name.value, img)

        for variable_name in EndsWithVariableFilenames:
            if filename.endswith(variable_name.value):
                name_img = (variable_name.name, img)

        images_with_corrected_names.append(name_img)

    central_slices = []
    for filename, arr in images_with_corrected_names:
        sq_arr = np.squeeze(arr)
        z_half = sq_arr.shape[-1] // 2
        central_slices.append((filename, sq_arr[..., z_half]))

    return OrderedDict(central_slices)


def get_table(slices: Mapping[str, np.ndarray]) -> wandb.Table:
    """
    Get a Weights & Biases table where
    each column is a central slice
    and has the filename as name.

    Args:
        slices: 2D slices.

    Returns:
        Weights and Biases table object.
    """
    plots = {}
    for name, sl in slices.items():
        img = sl / sl.max() if not np.isclose(sl.max(), 0) else sl
        fig = plt.imshow(img, cmap="hot")
        plots[name] = wandb.Image(fig)

    table = wandb.Table(columns=list(plots.keys()), data=[[plot for plot in plots.values()]])

    return table


def get_logs(path: Union[str, Path]) -> List[Path]:
    """
    Find all logfiles recursively based on file extension
    (extensions taken into account are provided by
    :py:class:`LogFileExtension`).

    Args:
        path: path to directory having logs.

    Returns:
        List with paths to logs.
    """
    return [logfile for logfile in Path(path).rglob("**/*") if logfile.suffix in [ext.value for ext in LogFileExtension]]


def save_cfg(cfg: Mapping[str, Any], path: Union[str, Path]) -> None:
    """
    Save the config part of the input
    config at given path.

    Args:
        cfg: ``dict``-like configuration.
        path: path to save the config.
    """
    path_ = Path(path)

    if path_.suffix not in set([".yaml", ".yml"]):
        scanner_cfg_save_path = path_.joinpath("config.yaml")
    else:
        scanner_cfg_save_path = path_

    with open(scanner_cfg_save_path, 'w') as s_cfg_path:
        yaml.dump(cfg, s_cfg_path, default_flow_style=False)


def copy_recon(cfg: Mapping[str, Any], path: Union[str, Path]) -> None:
    """
    Save the reconstruction image at the
    given path.

    Args:
        cfg: ``dict``-like configuration.
        path: path to save the config.
    """
    results_path = Path(cfg["dir_results_path"])

    try:
        recon_path = [p for p in results_path.rglob("**/rec_*.img") if p.name.startswith("rec_")].pop()
    except IndexError as ex:
        raise ex("Not reconstruction file found.")

    save_path = Path(path).joinpath(recon_path.name)
    save_path.parent.mkdir(exist_ok=True, parents=True)

    shutil.copy(recon_path, save_path)
    shutil.copy(recon_path.with_suffix(".hdr"), save_path.with_suffix(".hdr"))


try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
    OmegaConf.register_new_resolver("mibiolab_home_path", lambda s: "/home/mibiolab")
except ValueError:
    pass


@hydra.main(version_base=None, config_path=str(here().joinpath("configs")), config_name="config_test")
def simulate(cfg: DictConfig) -> None:

    OmegaConf.resolve(cfg)

    just_log = cfg.get("only_log")
    log = cfg.get("log")
    job_type = cfg.get("job_type_wandb")
    patient_dirname = cfg.get("params")["patient_dirname"]
    results_dir = Path(cfg["dir_results_path"])
    patient_dir = results_dir.joinpath(patient_dirname)

    try:
        remove_results_subdirs = cfg["params"]["remove_previous_patient_dir"]
    except KeyError:
        remove_results_subdirs = False

    if remove_results_subdirs:
        remove_dir_contents(patient_dir)

    if not just_log:
        test = simpet.SimPET(cfg)
        test.run()

    cfg = OmegaConf.to_container(cfg)

    if log:
        run = wandb.init(project="SimPET-Randfigs-Simulations", config=cfg, name=cfg["params"]["scanner"]["scanner_name"], job_type=job_type)
        data_central_slices = get_central_slices(cfg["dir_data_path"])
        outputs_central_slices = get_central_slices(cfg["dir_results_path"])
        
        data_table = get_table(data_central_slices)
        outputs_table = get_table(outputs_central_slices)
        run.log({"Data": data_table, "Outputs": outputs_table})

        logs_data = get_logs(cfg["dir_data_path"])
        logs_outputs = get_logs(cfg["dir_results_path"])
        logs = logs_data + logs_outputs

        logs_artifact = wandb.Artifact(name="Logs", type="Text-Files")
        for logf in set(logs):
            logs_artifact.add_file(local_path=logf, name=logf.name)

        run.log_artifact(logs_artifact)

    recon_name = [p.parents[1].name for p in patient_dir.rglob("**/rec_*.img") if p.name.startswith("rec_")].pop()
    recon_path = SAVE_IMAGE_PATH.joinpath(recon_name)

    copy_recon(cfg, recon_path)
    save_cfg(cfg, recon_path)


if __name__ == "__main__":
    simulate()
