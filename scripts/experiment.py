import sys
import hydra
import yaml
from typing import Union, Mapping, Any
from pathlib import Path
from pyprojroot import here
from omegaconf import DictConfig, OmegaConf

sys.path.append(str(here()))
import simpet


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


try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
    OmegaConf.register_new_resolver("home_path", lambda s: str(Path.home()))
except ValueError:
    pass


@hydra.main(version_base=None, config_path=str(here().joinpath("configs")), config_name="config_test")
def simulate(cfg: DictConfig) -> None:

    OmegaConf.resolve(cfg)

    patient_dirname = cfg.get("params")["patient_dirname"]
    results_dir = Path(cfg["dir_results_path"])
    patient_dir = results_dir.joinpath(patient_dirname)

    test = simpet.SimPET(cfg)
    test.run()

    cfg = OmegaConf.to_container(cfg)

    save_cfg(cfg, patient_dir)


if __name__ == "__main__":
    simulate()
