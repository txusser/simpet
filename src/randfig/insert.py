from typing import Sequence, Mapping, Any
from .config_transform import ConfigTransform


__all__ = ["Insert"]


class Insert(ConfigTransform):
    """
    Insert key, value pairs in the input configuration.

    .. exec_code::

        # --- hide: start ---
        from src.randfig import Insert
        # --- hide: stop ---

        init_config = {"param_0": 0, "param_1": 1}
        insert = Insert(keys=["param_2"], values=[2])

        # --- hide: start ---
        expected = {"param_0": 0, "param_1": 1, "param_2": 2}
        inserted = insert(init_config)
        assert inserted == expected, f":py:class:`src.randfig.Unnest` is not giving: {expected}, but {inserted}"
        print(inserted)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str], values: Sequence[Any]) -> None:
        """
        Args:
            values: values associated to :py:attr:`self.keys`.
                There must be one value per key.
        """
        super().__init__(keys)
        self.values = values

    def __call__(self, cfg: Mapping) -> Mapping:
        return {}

