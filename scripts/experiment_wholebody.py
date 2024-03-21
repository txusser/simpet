import sys
import hydra
from pathlib import Path
from pyprojroot import here
from omegaconf import DictConfig, OmegaConf

sys.path.append(str(here()))
import wholebody


try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
    OmegaConf.register_new_resolver("home_path", lambda s: str(Path.home()))
except ValueError:
    pass


@hydra.main(version_base=None, config_path=str(here().joinpath("configs")), config_name="config_test_wholebody")
def wholebody_simulation(cfg: DictConfig) -> None:
    OmegaConf.resolve(cfg)
    wb = wholebody.WholebodySimulation(cfg)
    wb.run()


if __name__ == "__main__":
    wholebody_simulation()
