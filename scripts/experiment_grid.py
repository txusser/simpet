import sys
import typer
import itertools
from omegaconf import OmegaConf
from hydra import compose, initialize
from pathlib import Path
from pyprojroot import here
from typing_extensions import Annotated

sys.path.append(str(here()))
import simpet


def main(
    data: Annotated[Path, typer.Option(exists=True, dir_okay=True, file_okay=False, resolve_path=True)],
    results: Annotated[Path, typer.Option(file_okay=False, resolve_path=True)]
):
    """
    # TODO
    """
    initialize(version_base=None, config_path="../configs", job_name="simpet")

    scanner_names = [s.stem for s in here().joinpath("configs/params/scanner").glob("scanner_*") if s.is_file()]
    data_subjects = [p.name for p in data.glob("*") if p.is_dir()]
    permutations = itertools.product(data_subjects, scanner_names)

    for subject, scanner in permutations:
        cfg = compose(
            config_name="randfig",
            overrides=[
                f"dir_data_path={str(data)}",
                f"dir_results_path={str(results)}",
                f"params/scanner={scanner}",
                f"params.patient_dirname='{subject}'",
                f"params.output_dir={subject}_{scanner}",
            ]
        )

        simulation = simpet.SimPET(cfg)
        simulation.run()

        scanner_name = cfg.params.scanner.scanner_name.replace(' ', '_').lower()
        patient_dirname = cfg.params.patient_dirname
        OmegaConf.save(cfg, results.joinpath(f"{patient_dirname}/{scanner_name}.yaml"))



if __name__ == "__main__":
    typer.run(main)
