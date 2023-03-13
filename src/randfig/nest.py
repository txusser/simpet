from typing import Mapping, Sequence
from config_transform import ConfigTransform


class Nest(ConfigTransform):

    def __init__(self, keys: Sequence[str], root: str) -> None:
        super().__init__(keys)
        self.root = root

    def __call__(self, cfg: Mapping) -> Mapping:
        self._check_mapping(cfg)
        self._check_keys(cfg)
        leaves = {k: v for k, v in cfg.items() if k in self.keys}
        cfg = {k: v for k, v in cfg.items() if k not in self.keys}
        cfg[self.root] = leaves
        return cfg
