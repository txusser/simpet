import pytest
import random
from src.randfig import Formula


def test_random(config):
    cfg = config
    rand_form = Formula(keys=["param_random"], formula=lambda cfg: random.randint(0, 9))
    cfg_rand = rand_form(cfg)

    assert "param_random" in cfg_rand.keys()
    assert cfg_rand["param_random"] in set(n for n in range(10))
    for k, v in cfg.items():
        assert cfg[k] == v


def test_sum(config):
    cfg = config
    sum_form = Formula(keys=["param_3"], formula=lambda cfg: cfg["param_1"] + cfg["param_2"])
    cfg_rand = sum_form(cfg)

    assert "param_3" in cfg_rand.keys()
    assert cfg_rand["param_3"] == cfg_rand["param_1"] + cfg_rand["param_2"]
    assert cfg_rand["param_3"] == cfg["param_1"] + cfg["param_2"]
    for k, v in cfg.items():
        assert cfg[k] == v
