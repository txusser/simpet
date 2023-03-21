from typing import Sequence, Mapping
from .config_transform import ConfigTransform


__all__ = ["Compose"]


class Compose:
    """
    Apply configuration trnasforms sequentially.
    """

    def __init__(self, transforms: Sequence[ConfigTransform]) -> None:
        """
        Args:
            transforms: a sequence of configuration
                tranforms that implement the
                :py:class:`randfig.config_transform.ConfigTransform`
                interface.
        """
        self.transforms = transforms

    def __call__(self, cfg: Mapping) -> Mapping:
        for tfs in self.transforms:
            cfg = tfs(cfg)
        return cfg
