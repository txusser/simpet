import hydra
from random import randint
from pathlib import Path
from omegaconf import DictConfig, OmegaConf



config_path = Path("../randfigs/config")


@hydra.main(
    config_path=config_path.parent, config_name=config_path.name, version_base=None
)
def main(cfg: DictConfig):
    """
    Generate random configs. 
    """
    OmegaConf.resolve(cfg)
    cfg = hydra.utils.instantiate(cfg, _recursive_=True)


if __name__ == '__main__':
    main()
