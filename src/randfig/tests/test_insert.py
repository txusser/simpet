import pytest
from src.randfig import Insert


@pytest.mark.parametrize('cfg,expected,keys,value', [
    [
        {"param_root_0": 0},
        {"param_root_0": 0, "param_root_1": 1},
        ["param_root_1"],
        1
    ]
])
def test_insert(cfg, expected, keys, value):
    insert = Insert(keys=keys, value=value)
    inserted = insert(cfg)
    assert expected == inserted
