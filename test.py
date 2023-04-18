import simpet
import hydra
from pyprojroot import here
from omegaconf import DictConfig, OmegaConf


try:
    OmegaConf.register_new_resolver("root_path", lambda s: str(here()))
except ValueError:
    pass


@hydra.main(version_base=None, config_path="configs", config_name="config_test")
def simulate(cfg: DictConfig) -> None:
    OmegaConf.resolve(cfg)
    test = simpet.SimPET(cfg)
    test.run()


if __name__ == "__main__":
    simulate()
