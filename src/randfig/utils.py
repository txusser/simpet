import operator
from collections import defaultdict
from functools import reduce
from typing import Mapping, Sequence, Any, DefaultDict, Dict


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
        print(nested_val)
        # --- hide: stop ---

    Args:
       mapping: an object following ``typing.Mapping`` interface.
       map_list: a sequence of nested keys.

    Returns:
        The value of the last key specified by ``map_list``.
    """
    return reduce(operator.getitem, map_list, mapping)


def mapping_to_defaultdict(mapping: Mapping[str, Any]) -> DefaultDict[str, Any]:
    """
    Convert a nested ``typing.Mapping`` to
    a nested ``typing.DefaultDict`` recursively.

    Args:
        mapping: nested ``typing.Mapping``.

    Returns:
        Nested ``typing.DefaultDict``.
    """
    if isinstance(mapping, Mapping):
        mapping = defaultdict(defaultdict, {k: mapping_to_defaultdict(v) for k, v in mapping.items()})
    return mapping


def mapping_to_dict(mapping: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Convert a nested ``typing.Mapping`` to
    a nested ``typing.Dict`` recursively.

    Args:
        mapping: nested ``typing.Mapping``.

    Returns:
        Nested ``typing.Dict``.
    """
    if isinstance(mapping, Mapping):
        mapping = {k: mapping_to_dict(v) for k, v in mapping.items()}
    return mapping


def insert_nested_key(cfg: Dict[str, Dict], keys: Sequence[str], value: Any) -> None:
    """
    Insert a key, value pair or update a value
    of a nested ``Mapping``.

    .. exec-code::

        # --- hide: start ---
        from src.randfig.utils import insert_nested_key
        # --- hide: stop ---

        cfg = {"param_root_0": {"param_00": "value_00", "param_01": "value_01"}}
        insert_nested_key(cfg, ["param_root_1", "param_10"], "value_10")

        # --- hide: start ---
        print(cfg)
        # --- hide: stop ---

    Args:
        cfg: nested ``Mapping``.
        keys: sequence of nested keys where ``value`` will be inserted.
        value: value to insert.

    Raises:
        TypeError: if one of the values of the nested keys is not a ``Mapping``.
    """
    if isinstance(cfg, Mapping):
        key = keys.pop(0)

        if not keys:
            cfg[key] = value
        else:
            insert_nested_key(cfg[key], keys, value)
    else:
        raise TypeError(f"Got: {cfg} for one of the nested values, which is {type(cfg)}, expected a``Mapping``.")


