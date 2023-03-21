from typing import Sequence, Mapping, Any
from .config_transform import ConfigTransform
from src.randfig.utils import insert_nested_key


__all__ = ["Insert"]


class Insert(ConfigTransform):
    """
    Insert key, value pairs in the input configuration.
    This class relies in :py:func:`src.randfig.utils.insert_nested_key`,
    see its documentation for detailed info.

    .. exec_code::

        # --- hide: start ---
        from src.randfig import Insert
        # --- hide: stop ---

        init_config = {"param_0": 0, "param_1": 1}
        inserted = Insert(keys=["param_2"], value=2)

        # --- hide: start ---
        print(inserted)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str], value: Any) -> None:
        """
        Args:
            keys: sequence of nested keys.
            value: value that will be inserted.
        """
        super().__init__(keys)
        self.value = value

    def __call__(self, cfg: Mapping) -> Mapping:
        insert_nested_key(cfg, self.keys, self.value)
        return cfg

