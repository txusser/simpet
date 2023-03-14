from typing import Mapping, Sequence
from .config_transform import ConfigTransform


__all__ = ["Nest"]


class Nest(ConfigTransform):
    """
    Nest a set of key, pair values
    under a root value as a ``dict``.

    .. exec_code::

        # --- hide: start ---
        from randfig.nest import Nest
        # --- hide: stop ---

        init_config = {"value_0": 1, "value_1": 2, "value_2": 3}
        nested = Nest(keys=["value_0", "value_1"], root="root")

        # --- hide: start ---
        expected = {"root": {"value_0": 1, "value_1": 2}, "value_2": 3}
        assert nested == expected, f":py:class:`randfig.Nest` is not giving: {expected}, but {nested}"
        print(nested)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str], root: str) -> None:
        """
        Args:
            root: the key, value paris specified by
                ``keys`` are nested under a key which
                name will be ``root``.
        """
        super().__init__(keys)
        self.root = root

    def __call__(self, cfg: Mapping) -> Mapping:
        """
        Nests ``keys`` under ``root``.

        Raises:
            ValueError: when :py:attr:`self.root` already
                exists in ``cfg`` as a key.
        """
        self._check_mapping(cfg)
        self._check_keys(cfg)
        
        if self.root not in cfg.keys():
            leaves = {k: v for k, v in cfg.items() if k in self.keys}
            cfg = {k: v for k, v in cfg.items() if k not in self.keys}
            cfg[self.root] = leaves
        else:
            raise ValueError(f"``root``: {self.root} already exists in ``cfg`` as a key.")

        return cfg
