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
    Typer app for grid-like experiments.
    The directory specified by ``data`` must
    have subjects-like structure: each subject
    must a have a folder with all its
    associated maps (activity and attenuation)
    in it.
    """
    initialize(version_base=None, config_path="../configs", job_name="simpet")

    scanner_names = [s.stem for s in here().joinpath("configs/params/scanner").glob("scanner_*") if s.is_file()]
    data_subjects = [p.name for p in data.glob("*") if p.is_dir()]

    # simulation dirs have the following name structure <subject_id>_scanner_<scanner_id>
    done_simulations = set([tuple(p.name.split("_", 1)) for p in results.glob("*") if p.is_dir()])
    permutations = set(itertools.product(data_subjects, scanner_names))

    # remove done simulations from possible simulations
    to_do_simulations = list(permutations - done_simulations)

    for subject, scanner in to_do_simulations:
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
        config_file_path = results.joinpath(cfg.output_dir).joinpath(f"{scanner_name}.yaml")
        config_file_path.touch()
        OmegaConf.save(cfg, config_file_path)


if __name__ == "__main__":
    typer.run(main)
