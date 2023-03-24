from typing import Callable, Any, Mapping


def accept_cfg(fn: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Callable[[Mapping, Any], Any]:
    """
    This decorator is intended to use it with functions like
    ``random.randint`` or ``random.uniform`` in facebook-hydra configurations.
    It aims to return a callable that accepts a ``dict``-like configuration
    and return a value. This way functions like ``random.randint`` or ``random.uniform``
    can be instantiated to pass them to the ``formula`` kwarg of :py:class:`src.randfig.formula.Formula`.
    For example:

    .. code-block::

        _target_: src.randfig.Formula
        keys: ["scanner_radius"]
        formula:
          _target_: src.randfig.decorators.accept_cfg
          _args_:
            - _target_: hydra.utils.get_method
              path: random.uniform
            - ${stats:scanner_radius_min}
            - ${stats:scanner_radius_max}

    Args:
        fn: a callable.
        args: arguments of that callable.
        kwargs: kwargs of that callable.

    Returns:
        A callable that accepts just a ``dict``-like configuration
        and returns ``fn(*args, **kwargs)``.
    """
    def fn_accepts_cfg(cfg):
        return fn(*args, **kwargs)

    return fn_accepts_cfg
