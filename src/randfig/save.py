import ruamel.yaml as yaml
from pathlib import Path
from typing import Sequence, Mapping, List, Union, Optional
from .config_transform import ConfigTransform
from src.randfig.utils import get_nested_value


__all__ = ["Save"]


class Save(ConfigTransform):
    """
    Saves the value of a sequence of nested keys
    as a YAML file, such value must be a ``typing.Mapping``.
    """

    def __init__(self,
        save_dir: Union[str, Path],
        filename: str,
        keys: Optional[Sequence[str]] = None,
        sequence: int = 2,
        offset: int = 4
    ) -> None:
        """
        Args:
            save_dir: path to dir where the configuration will be saved as YAML.
            filename: name of the file where the configuration will be saved. It
                must have ``".yaml"`` extension.
            sequence: ``ruamel.yaml`` parameter for ``YAML.indend`` method (avoid bad indents in lists).
            offset: ``ruamel.yaml`` parameter for ``YAML.indend`` method (avoid bad indents in lists).

        Raises:
            ValueError: ``filename`` has a path structure,
                that is it has parents: ``configs.yaml`` is valid, ``configs/config.yaml``
                is not valid.
            ValueError: if ``filename`` has an extension different from ``".yaml"``.
        """
        super().__init__(keys)
        self.save_dir = save_dir
        self.filename = filename
        self.save_path = self.save_dir.joinpath(self.filename)
        self.sequence = sequence
        self.offset = offset

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
        Returns:
            Input configuration without modifications.
        """
        self._check_mapping(cfg)
        nested_val = get_nested_value(cfg, self.keys) if self.keys is not None else cfg
        self._check_mapping(nested_val)

        self.save_path.unlink(missing_ok=True)

        with open(self.save_path, 'w') as nested_cfg_file:
            yml = yaml.YAML()
            yml.indent(sequence=self.sequence, offset=self.offset)
            yml.dump(nested_val, nested_cfg_file)

        return cfg
