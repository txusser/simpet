import pytest
from decimal import Decimal
import src.randfig.expressions as expressions


@pytest.mark.parametrize('cfg,key,element,expected', [
    [
        {"not_list": 1, "list": [1]},
        "list",
        0,
        1
    ],
    [
        {"not_list": 1, "list": [1, 2]},
        "list",
        1,
        2
    ]
])
def test_pop(cfg, key, element, expected):
    out = expressions.pop(cfg, key, element)
    assert out == expected


@pytest.mark.parametrize('cfg,key', [
    [
        {"not_list": 1, "list": [1]},
        "not_list"
    ],
    [
        {"not_list": 1, "list": [1, 2]},
        "not_list"
    ]
])
def test_pop_not_list(cfg, key):
    with pytest.raises(TypeError):
        expressions.pop(cfg, key, 0)


@pytest.mark.parametrize('cfg,key,expected,expected_decimals', [
    [
        {"not_number": "1", "number": 1.1111},
        "number",
        1.11,
        2
    ]
])
def test_rounding(cfg, key, expected, expected_decimals):
    out = expressions.rounding(cfg, key, expected_decimals)
    Decimal(str(out)).as_tuple().exponent == expected_decimals
    assert out == expected


@pytest.mark.parametrize('cfg,key', [
    [
        {"not_number": "1", "number": 1.1111},
        "not_number"
    ]
])
def test_rounding_not_number(cfg, key):
    with pytest.raises(TypeError):
        expressions.rounding(cfg, key, 0)
