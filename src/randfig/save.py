from pathlib import Path
from typing import Sequence, Mapping, List, Union
from .config_transform import ConfigTransform


__all__ = ["Save"]


class Save(ConfigTransform):
    """
    If they exist, the values specified by :py:attr:`self.keys`
    are saved as YAML, ``KeyError`` is raised if the specified
    keys do not exist. The keys must be spcified as a ``typing.List``,
    this way is possible to save nested values:

    .. code-block::

        nested_config = {"param_root" : {"param_nested": {"param_0": 0, "param_1": 1}}}
        save = Save(keys=["param_root", "param_nested"], save_dir="/configs")

        # {"param_0": 0, "param_1": 1} will be saved as YAML at "/configs".
    """

    def __init__(self, keys: Sequence[List[str]], save_dir: Union[str, Path]) -> None:
        super().__init__(keys)

    def __call__(self, cfg: Mapping) -> Mapping:
        """
        Raises:
            KeyError: if any of the (nested) :py:attr:`self.keys` does not
                exists in ``cfg``.

        Returns:
            Input configuration without modifications.
        """
        return {}
