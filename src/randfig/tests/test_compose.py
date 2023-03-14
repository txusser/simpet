import pytest
from src.randfig import Compose, Formula, Nest


def test_compose(config):
    cfg = config
    expected = {
        "param_root": {"param_0": 0, "param_1": 1},
        "param_2": 2,
        "param_3": cfg["param_1"] + cfg["param_2"]
    }
    transforms = Compose([
        Formula(keys=["param_3"], formula=lambda cfg: cfg["param_1"] + cfg["param_2"]),
        Nest(keys=["param_0", "param_1"], root="param_root")
    ])
    cfg_transforms = transforms(cfg)

    assert cfg_transforms == expected

