from numbers import Number
from typing import Mapping, Any, List


def pop(cfg: Mapping, key: str, element: int = 0) -> Any:
    """
    Pops an element of ``cfg[key]`` if
    its value is a ``List``. It is intended to use
    it with :py:func:`src.randfig.formula.Formula` and ``_partial_: true``
    in facebook-hydra configs.

    Args:
        cfg: ``dict``-like congifuration.
        key: a key of ``cfg`` which value is a ``List``
        element: which element to pop from the list.

    Returns:
        The poped element.

    Raises:
        TypeError: if the value associeted to
            ``cfg[key]`` is not a ``List``.
    """
    value_list = cfg[key]

    if not isinstance(value_list, List):
        raise TypeError(f"Expected a list but got {value_list} which is a {type(value_list)}.")

    return value_list.pop(element)


def rounding(cfg: Mapping, key: str, decimals: int) -> Any:
    """
    Round the value of ``cfg[key]`` if
    its value is a ``Number``. It is intended to use
    it with :py:func:`src.randfig.formula.Formula` and ``_partial_: true``
    in facebook-hydra configs.

    Args:
        cfg: ``dict``-like congifuration.
        key: a key of ``cfg`` which value is a ``Number``

    Returns:
        The rounded value.

    Raises:
        TypeError: if the value associeted to
            ``cfg[key]`` is not a ``Number``.
    """
    value_number = cfg[key]

    if not isinstance(value_number, Number):
        raise TypeError(f"Expected a numeric but got {value_number} which is a {type(value_number)}.")

    return round(value_number, decimals)
