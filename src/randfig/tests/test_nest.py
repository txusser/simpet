import pytest
from src.randfig import Nest


def test_nest(config):
    cfg = config
    expected = {"param_root": {"param_0": 0, "param_1": 1}, "param_2": 2}
    nest = Nest(keys=["param_0", "param_1"], root="param_root")
    cfg_nest = nest(cfg)

    assert cfg_nest == expected


def test_value_error_nest(config):
    cfg = config
    nest = Nest(keys=["param_0", "param_1"], root="param_2")

    with pytest.raises(ValueError):
        nest(cfg)
