import os
import simpet
import hydra
import wandb
import numpy as np
import nibabel as nib
from collections import OrderedDict
from typing import List, Union
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
    breakpoint()
    images = [(filename, nib.load(img_file).get_fdata()) for filename, img_file in image_files]

    central_slices = []
    for filename, arr in images:
        sq_arr = np.squeeze(arr)
        z_half = sq_arr.shape[-1] // 2
        central_slices.append((filename, sq_arr[..., z_half]))

    return OrderedDict(central_slices)


try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
except ValueError:
    pass


@hydra.main(version_base=None, config_path="configs", config_name="config_test")
def simulate(cfg: DictConfig) -> None:

    run = wandb.init(project="SimPET-Randfigs-Simulations", config=OmegaConf.to_container(cfg), name=cfg.params.scanner.scanner_name)

    OmegaConf.resolve(cfg)
    #test = simpet.SimPET(cfg)
    #test.run()

    data_central_slices = get_central_slices(cfg["dir_data_path"])
    breakpoint()
    outputs_central_slices = get_central_slices(cfg["dir_results_path"])

    data_table = wandb.Table(
        columns=list(data_central_slices.keys()),
        data=[[wandb.Image(img) for img in data_central_slices.values()]]
    )

    outputs_table = wandb.Table(
        columns=list(outputs_central_slices.keys()),
        data=[[wandb.Image(img) for img in outputs_central_slices.values()]]
    )

    run.log({"Data": data_table, "Outputs": outputs_table})


if __name__ == "__main__":
    simulate()
