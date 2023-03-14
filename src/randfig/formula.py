from typing import Callable, Mapping, Sequence
from .config_transform import ConfigTransform


__all__ = ["Formula"]


class Formula(ConfigTransform):
    """
    Compute a configuration value from a ``Callable[[Mapping], Mapping]``.
    For example:

    .. exec_code::

        # --- hide: start ---
        from randfig.formula import Formula
        # --- hide: stop ---

        init_config = {"value_0": 1}
        form = Formula(keys=["value_1"], formula: lambda cfg: 2 * cfg["value_0"])

        # --- hide: start ---
        expected = {"value_0": 1, "value_1", 2}
        assert form == expected, f":py:class:`randfig.Formula is not giving: {expected}, but {form}"
        print(form)
        # --- hide: stop ---
    """

    def __init__(self, keys: Sequence[str], formula: Callable[[Mapping], Mapping]) -> None:
        """
        Args:
            formula: a callable for computing ``keys``, the signature must be the
                one specified in the type hints, that is ``typing.Callable[[Mapping], Mapping]``.
                In order to follow that signature, ``functools.partial`` might help
                in most of cases.
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
