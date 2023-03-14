from abc import ABC, abstractmethod
from typing import Mapping, Any, Sequence


__all__ = ["ConfigTransform"]


class ConfigTransform(ABC):
    """
    Interface for tranformations that
    act on ``dict``-like configurations.
    """

    def __init__(self, keys: Sequence[str]) -> None:
        """
        Args:
            keys: concrete implementations of this
                interface will act on the keys
                given by this argument, leaving
                the rest of keys untransformed.
        """
        self.keys = keys

    def _check_keys(self, cfg: Mapping[str, Any]) -> None:
        """
        Checks the existance of :py:attr:`self.keys` in 
        ``cfg``.

        Args:
            cfg: ``dict``-like configuration.

        Raises:
            KeyError: when one of the keys in :py:attr:`self.keys` is not in ``cfg`` keys.
        """
        cfg_keys = cfg.keys()
        for k in self.keys:
            if k not in cfg_keys:
                raise KeyError(f"Key {k} not found in self.keys: {self.keys}")

    def _check_mapping(self, cfg: Mapping[str, Any]) -> None:
        """
        Checks if ``cfg`` follows ``typing.Mapping`` interface.

        Args:
            cfg: a ``dict``-like configuration.

        Raises:
            TypeError: if ``cfg`` does not follows ``typing.Mapping`` interface.

        """
        if not isinstance(cfg, Mapping):
            raise TypeError(f"cfg is not a Mapping, cfg is: {type(cfg)}")

    @abstractmethod
    def __call__(self, cfg: Mapping) -> Mapping:
        """
        Concrete implementations must override
        this method in order to define how
        ``cfg`` is transformed.

        Args:
            cfg: a ``dict``-like configuration.
        """
        pass
