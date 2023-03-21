from typing import Sequence, Mapping
from .config_transform import ConfigTransform
from src.randfig.utils import remove_nested_key


__all__ = ["Remove"]


class Remove(ConfigTransform):
    """
    If they exist, remove key, value pairs specified by
    :py:attr:`self.keys`. This class relies on
    :py:func:`src.randfig.remove_nested_key`, see its
    documentation for detailed info.

    .. exec_code::

        # --- hide: start ---
        from src.randfig import Remove
        # --- hide: stop ---

        init_config = {"param_0": 0, "param_1": 1, "param_2": 2}
        remove = Remove(keys=["param_2"])
        removed = remove(init_config)

        # --- hide: start ---
        print(removed)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str]) -> None:
        super().__init__(keys)

    def __call__(self, cfg: Mapping) -> Mapping:
        remove_nested_key(cfg, self.keys)
        return cfg

