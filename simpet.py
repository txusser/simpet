import os
import sys
import shutil
from pathlib import Path
from os.path import join, exists
from omegaconf import DictConfig, OmegaConf
from pyprojroot import here
from utils import tools
from src.simset import simset_sim as sim


class SimPET(object):
    """
    This class provides main SimPET functions.
    You have to initialize the class with a params file.
    Before using SimPET, check out the README.

    """

    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = OmegaConf.to_container(cfg)
        self.simpet_dir = here()
        self.config = {k: v for k, v in self.cfg.items() if k != "params"}
        self.params = self.cfg["params"]
        self.sim_type = self.params["sim_type"]
        self.scanner = self.params["scanner"]
        self.scanner_model = (
            self.params["scanner"]["scanner_name"].replace(" ", "_").lower()
        )

        if self.cfg["dir_data_path"] is not None:
            self.dir_data = Path(self.cfg["dir_data_path"])
        else:
            self.dir_data = here().joinpath("Data")

        if self.cfg["dir_results_path"] is not None:
            self.dir_results = Path(self.cfg["dir_results_path"])
        else:
            self.dir_results = here().joinpath("Data")

        self.act_map = self.dir_data.joinpath(self.params["patient_dirname"]).joinpath(
            self.params["act_map"]
        )
        self.att_map = self.dir_data.joinpath(self.params["patient_dirname"]).joinpath(
            self.params["att_map"]
        )
        self.output_dir = self.dir_results.joinpath(self.params["output_dir"])
        self.log_file = self.output_dir.joinpath("logfile.log")
        self.maps_dir = self.output_dir.joinpath("Maps")

        make_dirs = [self.dir_data, self.dir_results, self.output_dir, self.maps_dir]

        for dir_ in make_dirs:
            dir_.mkdir(parents=True, exist_ok=True)

    def simset_simulation(self, act_map, att_map):
        projections_dir = str(
            self.output_dir.joinpath("SimSET_Sim_" + self.scanner_model)
        )

        if self.params.get("do_simulation") == 1:
            if exists(projections_dir):
                if self.config.get("interactive_mode") == 1:
                    print(
                        "The introduced output dir already has a SimSET simulation.Proceeding will delete it."
                    )
                    remove = input(" Write 'Y' to delete it: ")
                    print(
                        "You can disable this prompt by deactivating interactive mode in the config file."
                    )
                    if remove == "Y":
                        shutil.rmtree(projections_dir)
                    else:
                        raise Exception("The simulation was aborted.")
                        ## Place some logging here
                        sys.exit(1)
                else:
                    shutil.rmtree(projections_dir)

            os.makedirs(projections_dir)

            my_simulation = sim.SimSET_Simulation(
                self.params,
                self.config,
                act_map,
                att_map,
                self.scanner,
                projections_dir,
            )
            my_simulation.run()

        if self.params.get("do_reconstruction") == 1:
            reconstruction_type = self.scanner.get("recons_type")

            if not exists(projections_dir):
                raise Exception(
                    "The projections directory does not exist. Run your simulation first."
                )
                ## Place some logging here
                sys.exit(1)

            postprocess_log = join(projections_dir, "postprocessing.log")

            # If it is a new simulation or if the trues.hdr were not added previously, it makes the postprocessing
            if not exists(postprocess_log):
                print(
                    "Your simulation SimSET outputs were not processed previously. We will try it now..."
                )
                my_simulation = sim.SimSET_Simulation(
                    self.params,
                    self.config,
                    act_map,
                    att_map,
                    self.scanner,
                    projections_dir,
                )
                my_simulation.simulation_postprocessing()

            reconstruction_dir = join(projections_dir, reconstruction_type)

            if exists(reconstruction_dir):
                if self.config.get("interactive_mode") == 1:
                    print(
                        "The introduced output dir already has a %s reconstruction.Proceeding will delete it."
                        % reconstruction_type
                    )
                    remove = input(" Write 'Y' to delete it: ")
                    print(
                        "You can disable this prompt by deactivating interactive mode in the config file."
                    )
                    if remove == "Y":
                        shutil.rmtree(reconstruction_dir)
                    else:
                        raise Exception("The simulation was aborted.")
                        ## Place some logging here
                        sys.exit(1)
                else:
                    shutil.rmtree(reconstruction_dir)

            my_reconstruction = sim.SimSET_Reconstruction(
                self.params,
                self.config,
                projections_dir,
                self.scanner,
                reconstruction_dir,
                reconstruction_type,
            )
            my_reconstruction.run()

    def run(self):
        act_map, att_map = tools.convert_map_values(
            str(self.act_map),
            str(self.att_map),
            str(self.maps_dir),
            str(self.log_file),
            mode=self.sim_type,
        )

        if self.sim_type == "SimSET":
            self.simset_simulation(act_map, att_map)
