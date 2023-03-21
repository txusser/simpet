import pytest
import yaml
from src.randfig import Save


@pytest.mark.parametrize("keys,expected_from_yaml",
    [
        (["param_root"], {"param_nest": {"param_0": 0, "param_1": 1}}),
        (["param_root", "param_nest"], {"param_0": 0, "param_1": 1}),
    ])
def test_save(tmp_path, nested_config, keys, expected_from_yaml):
    filename = "config.yaml"
    save = Save(keys=keys, save_dir=tmp_path, filename=filename)
    cfg = save(nested_config)

    assert tmp_path.joinpath(filename).is_file()

    with open(tmp_path.joinpath(filename), "r") as cfg_file:
        out_cfg = yaml.safe_load(cfg_file)

    assert expected_from_yaml == out_cfg
    assert cfg == nested_config


@pytest.mark.parametrize("keys",
    [
        ["param_root_fake"],
        ["param_root", "param_nest_fake"]
    ])
def test_key_not_exists(tmp_path, nested_config, keys):
    filename = "config.yaml"
    save = Save(keys=keys, save_dir=tmp_path, filename=filename)

    with pytest.raises(KeyError):
        save(nested_config)


@pytest.mark.parametrize("ext", [".yml", ".txt", ".nii.gz"])
def test_wrong_file_extension(tmp_path, ext):
    filename = "config" + ext

    with pytest.raises(ValueError):
        Save(keys=["params_root"], save_dir=tmp_path, filename=filename)


def test_filename_is_path(tmp_path):
    filename = tmp_path.joinpath("config.yaml")

    with pytest.raises(ValueError):
        Save(keys=["params_root"], save_dir=tmp_path, filename=filename)


def test_wrong_key_order(tmp_path, nested_config):
    filename = "config.yaml"
    save = Save(keys=["param_nest", "param_root"], save_dir=tmp_path, filename=filename)

    with pytest.raises(KeyError):
        save(nested_config)


def test_value_is_not_mapping(tmp_path):
    filename = "config.yaml"
    not_nested_cfg = {"param_root": 0}
    save = Save(keys=["param_root"], save_dir=tmp_path, filename=filename)

    with pytest.raises(TypeError):
        save(not_nested_cfg)


def test_keys_is_not_sequence(config, tmp_path):
    with pytest.raises(TypeError):
        Save(keys={}, save_dir=tmp_path, filename=tmp_path.joinpath("test.yaml"))

