from typing import Callable, Mapping, Sequence
from config_transform import ConfigTransform


class Formula(ConfigTransform):

    def __init__(self, keys: Sequence[str], formula: Callable[[Mapping], Mapping]) -> None:
        super().__init__(keys)
        self.formula = formula

    def __call__(self, cfg: Mapping) -> Mapping:
        self._check_mapping(cfg)
        for key in self.keys:
            cfg[key] = self.formula(cfg)
        return cfg
