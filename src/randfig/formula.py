from typing import Callable, Mapping, Sequence, Any
from .config_transform import ConfigTransform


__all__ = ["Formula"]


class Formula(ConfigTransform):
    """
    Compute a configuration value from a ``Callable[[Mapping], Any]``.
    For example:

    .. exec_code::

        # --- hide: start ---
        from src.randfig.formula import Formula
        # --- hide: stop ---

        init_config = {"param_0": 1}
        form = Formula(keys=["param_1"], formula: lambda cfg: 2 * cfg["param_0"])

        # --- hide: start ---
        expected = {"param_0": 1, "param_1", 2}
        out = form(init_config)
        assert out == expected, f":py:class:`src.randfig.Formula is not giving: {expected}, but {out}"
        print(out)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str], formula: Callable[[Mapping], Any]) -> None:
        """
        Args:
            formula: a callable for computing ``keys``, the signature must be the
                one specified in the type hints, that is ``typing.Callable[[Mapping], Any]``.
                In order to follow that signature, ``functools.partial`` might help
                in most cases.
        """
        super().__init__(keys)
        self.formula = formula

    def __call__(self, cfg: Mapping) -> Mapping:
        """
        Compute the new keys specified by ``keys``
        following the operation defined by ``formula``.
        """
        self._check_mapping(cfg)
        for key in self.keys:
            cfg[key] = self.formula(cfg)
        return cfg
