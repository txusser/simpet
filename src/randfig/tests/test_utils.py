import pytest
import src.randfig.utils as utils


@pytest.mark.parametrize("mapping,map_list,expected",
    [
        (
            {"param_nested": 0},
            ["param_nested"],
            0
        ),
        (
            {"param_root": {"param_nested": {"param_0": 0, "param_1": 1}}},
            ["param_root", "param_nested"],
            {"param_0": 0, "param_1": 1}
        ),
        (
            {"param_root": {"param_nested": {"param_0": 0, "param_1": 1}}},
            ["param_root", "param_nested", "param_0"],
            0
        )
    ])
def test_get_nested_value(mapping, map_list, expected):
    nested_val = utils.get_nested_value(mapping, map_list)
    assert nested_val == expected

