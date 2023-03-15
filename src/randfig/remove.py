from typing import Sequence, Mapping
from .config_transform import ConfigTransform


__all__ = ["Remove"]


class Remove(ConfigTransform):
    """
    If they exist, remove key, value pairs specified by
    :py:attr:`self.keys`, otherwise ``KeyError`` is raised.

    .. exec_code::

        # --- hide: start ---
        from src.randfig import Remove
        # --- hide: stop ---

        init_config = {"param_0": 0, "param_1": 1, "param_2": 2}
        remove = Remove(keys=["param_2"])

        # --- hide: start ---
        expected = {"param_0": 0, "param_1": 1}
        removed = remove(init_config)
        assert removed == expected, f":py:class:`src.randfig.Unnest` is not giving: {expected}, but {removed}"
        print(removed)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str]) -> None:
        super().__init__(keys)

    def __call__(self, cfg: Mapping) -> Mapping:
        """
        Raises:
            KeyError: if any of the given :py:attr:`self.keys` does not
                exists in ``cfg``.
        """
        return {}

