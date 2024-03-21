import sys
import hydra
from pathlib import Path
from pyprojroot import here
from omegaconf import DictConfig, OmegaConf

sys.path.append(str(here()))
import brainviset


try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
    OmegaConf.register_new_resolver("home_path", lambda s: str(Path.home()))
except ValueError:
    pass


@hydra.main(version_base=None, config_path=str(here().joinpath("configs")), config_name="config_test_brainviset")
def run_brainviset(cfg: DictConfig) -> None:
    OmegaConf.resolve(cfg)
    bviset = brainviset.BrainVISET(cfg)
    bviset.run()


if __name__ == "__main__":
    run_brainviset()
