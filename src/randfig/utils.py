import operator
from functools import reduce
from typing import Mapping, Sequence, Any


def get_nested_value(mapping: Mapping, map_list: Sequence[str]) -> Any:
    """
    Get the value of nested keys.

    .. exec-code::

        # --- hide: start ---
        from src.randfig.utils import get_nested_value
        # --- hide: stop ---


        nested = {"param_root": {"param_nested": {"param_1": 1, "param_2": 2}}}
        nested_val = get_nested_value(nested, ["param_root", "param_nested"])

        # --- hide: start ---
        expected = {"param_1": 1, "param_2": 2}
        assert expected == nested_val, f":py:func:`src.randfig.utils.get_nested_value` is giving: {nested_val} but expected: {expected}"
        print(nested_val)
        # --- hide: stop ---

    Args:
       mapping: an object following ``typing.Mapping`` interface.
       map_list: a sequence of nested keys.

    Returns:
        The value of the last key specified by ``map_list``.
    """
    return reduce(operator.getitem, map_list, mapping)
