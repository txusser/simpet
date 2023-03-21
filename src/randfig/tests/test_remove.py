import pytest
from src.randfig import Remove


@pytest.mark.parametrize('cfg,expected,keys', [
    [
        {"param_root_0": 0, "param_root_1": 1},
        {"param_root_0": 0},
        ["param_root_1"],
    ]
])
def test_insert(cfg, expected, keys):
    remove = Remove(keys=keys)
    removed = remove(cfg)
    assert removed == expected
