import typer
import wandb
import nibabel as nib
from enum import Enum


class Extension(Enum):
    """
    # TODO
    """
    Ni


def main(
    results_dir: Path = typer.Option(exists=True, file_ok=False, dir_ok=True, resolve_path=True),
    experiment_name: typer.Argument(...)
) -> None:
    """
    # TODO
    """
    pass
    

if __name__=='__main__':
    typer.run(main)


