import pytest
import random
import src.randfig.decorators as decorators


@pytest.mark.parametrize('fn,dtype,args,kwargs', [
    [random.randint, int, [0, 10], {}],
    [random.uniform, float, [], {"a": 0, "b": 10}]
])
def test_accept_cfg(config, fn, dtype, args, kwargs):
    decorated_fn = decorators.accept_cfg(fn, *args, **kwargs)
    out = decorated_fn(config)

    assert isinstance(out, dtype)


def test_accept_cfg_as_decorator(config):
    
    @decorators.accept_cfg
    def fn(*args, **kwargs):
        return 0
    
    assert fn(config) == 0

