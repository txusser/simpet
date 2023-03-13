from typing import Sequence, Mapping
from config_transform import ConfigTransform


class Compose:

    def __init__(self, transforms: Sequence[ConfigTransform]) -> None:
        self.transforms = transforms

    def __call__(self, cfg: Mapping) -> Mapping:
        for tfs in self.transforms:
            cfg = tfs(cfg)
        return cfg
