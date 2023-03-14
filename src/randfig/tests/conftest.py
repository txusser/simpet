import pytest


@pytest.fixture(scope="module")
def config():
    return {"param_0": 0, "param_1": 1, "param_2": 2}

