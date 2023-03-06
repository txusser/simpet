import simpet
import hydra
from omegaconf import DictConfig, OmegaConf


@hydra.main(version_base=None, config_path="configs", config_name="config")
def simulate(cfg: DictConfig) -> None:
    test = simpet.SimPET(cfg)
    test.run()


if __name__ == "__main__":
    simulate()
