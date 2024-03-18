import os
import yaml
import sys
from os.path import join, exists
from omegaconf import DictConfig, OmegaConf
from pyprojroot import here
from utils import tools
from utils import wb_tools

sys.path.append(str(here()))
from simpet import SimPET


class WholebodySimulation(object):
    """
    This class provides functionalities to simulate several beds.
    You have to initialize the class with a params file. The class will iteratively call the SimPET class.
    Before using SimPET, check out the README.

    """

    def __init__(self, cfg: DictConfig):

        # Initialization
        self.simpet_dir = here()
        self.cfg_omega= cfg
        self.cfg = OmegaConf.to_container(cfg)
        self.params = self.cfg["params"]
        self.config = {k: v for k, v in self.cfg.items() if k != "params"}
        self.scanner = self.cfg["params"]["scanner"]
        self.scanner_model = self.params.get("scanner")

        # The following lines will read the general, scanner and config parameters
        self.sim_type = self.params.get("sim_type")
        self.zmin = self.params.get("z_min")
        self.zmax = self.params.get("z_max")

        # This will load the environment config
        self.cesga = self.config.get("cesga")

        if self.cesga:
            self.dir_data = self.config.get("cesga_data_path")
        else:
            self.dir_data = self.config.get("dir_data_path")
            if not self.dir_data:
                self.dir_data = join(self.simpet_dir, "Data")

        if self.cesga:
            self.dir_results = self.config.get("cesga_results_path")
        else:
            self.dir_results = self.config.get("dir_results_path")
            if not self.dir_results:
                self.dir_results = join(self.simpet_dir, "Results")
        if not exists(self.dir_results):
            os.makedirs(self.dir_results)

    def run(self):

        patient_dir = self.params.get("patient_dirname")
        act_map = join(self.dir_data, patient_dir, self.params.get("act_map"))
        att_map = join(self.dir_data, patient_dir, self.params.get("att_map"))
        output_name = self.params.get("output_dir")
        output_dir = join(self.dir_results, output_name)
        maps_dir = join(output_dir, "Maps")

        # THIS WILL POP UP EVEN IF ONLY RECONSTRUCTION IS DONE. MOVE IT OUT
        if not exists(output_dir):
            os.makedirs(output_dir)

        log_file = join(output_dir, "logfile.log")

        beds_cs = wb_tools.calculate_center_slices(act_map, self.scanner, self.zmin, self.zmax)

        print("The number of beds to simulate is: %s" % len(beds_cs))
        print("Beds center slides: %s" % beds_cs)

        j = 1

        for cs in beds_cs:

            bed_dir = join(output_dir, "Bed_cs_%s" % cs)
            if not exists(bed_dir):
                os.makedirs(bed_dir)

            self.params['center_slice'] = cs
            self.params['output_dir'] = output_name + "/Bed_cs_%s" % cs

            print("Simulating bed %s with center slice %s" % (j, cs))

            bed_simu = SimPET(self.cfg_omega)
            bed_simu.run()

        recons_beds = []
        recons_algorithm = self.scanner.get('recons_type')
        recons_it = self.scanner.get('numberOfIterations')

        for cs in beds_cs:
            recons_dir = join(output_dir, "Bed_cs_%s" % cs, "%s_Sim_%s" % (self.sim_type, self.scanner_model),
                              recons_algorithm)
            recons_file = join(recons_dir, 'rec_%s_%s.hdr' % (recons_algorithm, recons_it))
            recons_beds.append(recons_file)

        joint_beds = join(output_dir, 'rec_%s_%s.hdr' % (recons_algorithm, recons_it))
        wb_tools.join_beds_wb(recons_beds, joint_beds)
