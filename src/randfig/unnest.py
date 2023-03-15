from typing import Sequence, Mapping
from .config_transform import ConfigTransform


__all__ = ["Unnest"]


class Unnest(ConfigTransform):
    """
    If the values of the keys specified by
    :py:attr:`self.keys` are ``typing.Mapping``s
    they are unnested. Then :py:attr:`self.keys` are
    deleted from the input configuration.

    .. exec_code::

        # --- hide: start ---
        from src.randfig import Unnest
        # --- hide: stop ---

        init_config = {"param_0": 0, "param_root": {"param_1": 1, "param_2": 2}}
        unnest = Unnest(keys=["param_root"])

        # --- hide: start ---
        expected = {"param_0": 0, "param_1": 1, "param_2": 2}
        unnested = unnest(init_config)
        assert unnested == expected, f":py:class:`src.randfig.Unnest` is not giving: {expected}, but {unnested}"
        print(unnested)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str]) -> None:
        super().__init__(keys)

    def __call__(self, cfg: Mapping) -> Mapping:
        return {}

