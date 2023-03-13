from abc import ABC, abstractmethod
from typing import Mapping, Any


class ConfigTransform(ABC):

    def __init__(self, keys: Mapping) -> None:
        self.keys = keys

    def _check_keys(self, cfg: Mapping[str, Any]) -> None:
        cfg_keys = cfg.keys()
        for k in self.keys:
            if k not in cfg_keys:
                raise KeyError(f"Key {k} not found in self.keys: {self.keys}")

    def _check_mapping(self, cfg: Mapping[str, Any]) -> None:
        if not isinstance(cfg, Mapping):
            raise TypeError(f"cfg is not a Mapping, cfg is: {type(cfg)}")

    @abstractmethod
    def __call__(self, cfg: Mapping) -> Mapping:
        pass
