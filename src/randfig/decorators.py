from typing import Callable, Any, Mapping


def accept_cfg(fn: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Callable[[Mapping, Any], Any]:
    """
    Stub.

    Args:

    Returns:
    """
    def fn_accepts_cfg(cfg):
        return fn(*args, **kwargs)

    return fn_accepts_cfg
