import yaml
from pathlib import Path
from typing import Sequence, Mapping, List, Union
from .config_transform import ConfigTransform
from src.randfig.utils import get_nested_value


__all__ = ["Save"]


class Save(ConfigTransform):
    """
    Saves the value of a sequence of nested keys
    as a YAML file, such value must be a ``typing.Mapping``.

    .. code-block::

        nested_config = {"param_root" : {"param_nested": {"param_0": 0, "param_1": 1}}}
        save = Save(keys=["param_root", "param_nested"], save_dir="/configs", filename="config.yaml")

        # {"param_0": 0, "param_1": 1} will be saved as YAML at "/configs/config.yaml".
    """

    def __init__(self, keys: Sequence[str], save_dir: Union[str, Path], filename: str) -> None:
        """
        Args:
            save_dir: path to dir where the configuration will be saved as YAML.
            filename: name of the file where the configuration will be saved. It
                must have ``".yaml"`` extension.

        Raises:
            ValueError: if :py:attr:`self.filename` has a path structure,
                that is it has parents: ``configs.yaml`` is valid, ``configs/config.yaml``
                is not valid.
            ValueError: if :py:attr:`self.filename` has an extension different from ``".yaml"``.
        """
        super().__init__(keys)
        self.save_dir = save_dir
        self.filename = filename
        self.save_path = self.save_dir.joinpath(self.filename)

    @property
    def save_dir(self):
        return self._save_dir

    @save_dir.setter
    def save_dir(self, value):
        self._save_dir = Path(value)
        self._save_dir.mkdir(exist_ok=True, parents=True)
        return self._save_dir

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = Path(value)

        if self._filename.parent.name:
            raise ValueError(f"It seems like provided filename is a path: {str(self._filename)}.")

        file_ext = self._filename.suffix
        expected_ext = ".yaml"

        if file_ext != expected_ext:
            raise ValueError(f"Provided filename has extension {file_ext}, but expected {expected_ext}.")
        return self._filename

    def __call__(self, cfg: Mapping) -> Mapping:
        """
        Raises:
            KeyError: if any of the (nested) :py:attr:`self.keys` does not
                exists in ``cfg``.
            TypeError: if the retrived value (the one associated with the last nested key) is not a ``typing.Mapping``.

        Returns:
            Input configuration without modifications.
        """
        self._check_mapping(cfg)
        nested_val = get_nested_value(cfg, self.keys)
        self._check_mapping(nested_val)

        self.save_path.unlink(missing_ok=True)

        with open(self.save_path, 'w') as nested_cfg_file:
            yaml.dump(nested_val, nested_cfg_file)

        return cfg
