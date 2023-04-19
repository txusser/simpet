import os
import simpet
import hydra
import wandb
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib import cm
from collections import OrderedDict
from typing import List, Union, Sequence, Mapping
from enum import Enum
from pathlib import Path
from pyprojroot import here
from omegaconf import DictConfig, OmegaConf


# TODO: collor paletter and docstrings


class ImageExtension(Enum):
    """
    # TODO
    """
    NIFTI = '.nii'
    NIFTI_GZ = '.nii.gz'
    ANALYZE = '.img'


class LogFileExtension(Enum):
    """
    # TODO
    """
    LOG = '.log'
    TXT = '.txt'


def get_central_slices(path: Union[str, Path]) -> OrderedDict[str, np.ndarray]:
    """
    Stub.

    Args:
        path:

    Returns:
    """
    path_ = Path(path)

    image_extensions = [ext.value for ext  in ImageExtension]
    image_files = [(file_.name, file_) for file_ in path_.rglob("**/*") if "".join(file_.suffixes) in image_extensions]
    images = [(filename, nib.load(img_file).get_fdata()) for filename, img_file in image_files]

    central_slices = []
    for filename, arr in images:
        sq_arr = np.squeeze(arr)
        z_half = sq_arr.shape[-1] // 2
        central_slices.append((filename, sq_arr[..., z_half]))

    return OrderedDict(central_slices)


def get_table(slices: Mapping[str, np.ndarray]) -> wandb.Table:
    """
    Stub.

    Args:
        slices:

    Returns:
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
    Stub.

    Args:
        path:

    Returns:
    """
    return [logfile for logfile in Path(path).rglob("**/*") if logfile.suffix in [ext.value for ext in LogFileExtension]]

        

try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
except ValueError:
    pass


@hydra.main(version_base=None, config_path="configs", config_name="config_test")
def simulate(cfg: DictConfig) -> None:

    OmegaConf.resolve(cfg)

    just_log = cfg["only_log"]

    if not just_log:
        test = simpet.SimPET(cfg)
        test.run()

    cfg = OmegaConf.to_container(cfg)
    run = wandb.init(project="SimPET-Randfigs-Simulations", config=cfg, name=cfg["params"]["scanner"]["scanner_name"])

    data_central_slices = get_central_slices(cfg["dir_data_path"])
    outputs_central_slices = get_central_slices(cfg["dir_results_path"])
    
    data_table = get_table(data_central_slices)
    outputs_table = get_table(outputs_central_slices)
    run.log({"Data": data_table, "Outputs": outputs_table})

    logs_data = get_logs(cfg["dir_data_path"])
    logs_outputs = get_logs(cfg["dir_results_path"])
    logs = logs_data + logs_outputs

    logs_artifact = wandb.Artifact(name="Logs", type="Text-Files")
    for logf in logs:
        logs_artifact.add_file(local_path=logf, name=logf.name)

    run.log_artifact(logs_artifact)


if __name__ == "__main__":
    simulate()
