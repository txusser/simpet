#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join, dirname, abspath, isdir, exists
import os, sys
import shutil
import datetime
from utils import resources as rsc
from utils import tools
import yaml

class SimPET(object):
    """
    This class provides main SimPET functions.
    You have to initialize the class with a params file.
    Before using SimPET, check out the README.

    """

    def __init__(self,param_file,config_file="config.yml"):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))
        self.dir_data = join(self.simpet_dir, "Data")
        self.dir_results = join(self.simpet_dir, "Results")
        if not exists(self.dir_results):
            os.makedirs(self.dir_results)

        # The following lines will read the general, scanner and config parameters
        with open(param_file, 'rb') as f:
            self.params = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.sim_type = self.params.get("sim_type")

        # This will load the scanner params for the selected scanner
        self.scanner_model = self.params.get("scanner")
        scanner_parfile = join(self.simpet_dir,"scanners",self.scanner_model + ".yml")
        with open(scanner_parfile, 'rb') as f:
            self.scanner = yaml.load(f.read(), Loader=yaml.FullLoader)

        # This will load the environment config
        with open(config_file, 'rb') as f:
            self.config = yaml.load(f.read(), Loader=yaml.FullLoader)

        #SPM variables (Only used to create initial maps from patient data)
        self.matlab_mcr_path = self.config.get("matlab_mcr_path")
        self.spm_path = self.config.get("spm_path")
        self.spm_run = "sh %s/run_spm12.sh %s batch" % (self.spm_path, self.matlab_mcr_path)

    def simset_simulation(self,act_map,att_map,output_dir):

        projections_dir = join(output_dir, "SimSET_Sim_" + self.scanner_model)

        from src.simset import simset_sim as sim

        if self.params.get("do_simulation")==1:

            if exists(projections_dir):
                if self.config.get("interactive_mode")==1:
                    print("The introduced output dir already has a SimSET simulation.Proceeding will delete it.")
                    remove = raw_input(" Write 'Y' to delete it: ")
                    print("You can disable this prompt by deactivating interactive mode in the config file.")
                    if remove == "Y":
                        shutil.rmtree(projections_dir)
                    else:
                        raise Exception('The simulation was aborted.')
                        ## Place some logging here
                        sys.exit(1)
                else:
                    shutil.rmtree(projections_dir)

            os.makedirs(projections_dir)

            my_simulation = sim.SimSET_Simulation(self.params,self.config,act_map,att_map, self.scanner,projections_dir)
            my_simulation.run()

        if self.params.get("do_reconstruction")==1:

            reconstruction_type = self.scanner.get("recons_type")

            if not exists (projections_dir):
                    raise Exception('The projections directory does not exist. Run your simulation first.')
                    ## Place some logging here
                    sys.exit(1)

            postprocess_log = join(projections_dir,"postprocessing.log")

            # If it is a new simulation or if the trues.hdr were not added previously, it makes the postprocessing
            if not exists (postprocess_log):
                print("Your simulation SimSET outputs were not processed previously. We will try it now...")
                my_simulation = sim.SimSET_Simulation(self.params,self.config,act_map,att_map, self.scanner,projections_dir)
                my_simulation.simulation_postprocessing()

            reconstruction_dir = join(output_dir, "SimSET_STIR_" + reconstruction_type)

            if exists(reconstruction_dir):
                if self.config.get("interactive_mode")==1:
                    print("The introduced output dir already has a %s reconstruction.Proceeding will delete it." % reconstruction_type)
                    remove = raw_input(" Write 'Y' to delete it: ")
                    print("You can disable this prompt by deactivating interactive mode in the config file.")
                    if remove == "Y":
                        shutil.rmtree(reconstruction_dir)
                    else:
                        raise Exception('The simulation was aborted.')
                        ## Place some logging here
                        sys.exit(1)
                else:
                    shutil.rmtree(reconstruction_dir)

            my_reconstruction = sim.SimSET_Reconstruction(self.params,self.config,projections_dir,self.scanner,reconstruction_dir,reconstruction_type)
            my_reconstruction.run()

    def stir_simulation(self,param_file):

        from src.stir import stir_sim as sim

    def run(self):

        from utils import tools

        patient_dir = self.params.get("patient_dirname")
        act_map = join(self.dir_data, patient_dir, self.params.get("act_map"))
        att_map = join(self.dir_data, patient_dir, self.params.get("att_map"))
        output_dir = join(self.dir_results,self.params.get("output_dir"))
        maps_dir = join(output_dir,"Maps")

        # THIS WILL POP UP EVEN IF ONLY RECONSTRUCTION IS DONE. MOVE IT OUT
        if not exists(output_dir):
            os.makedirs(output_dir)
            os.makedirs(maps_dir)

        log_file = join(output_dir,"logfile.log")

        act_map, att_map = tools.convert_map_values(act_map,att_map,maps_dir,log_file,mode=self.sim_type)

        if self.sim_type=="SimSET":

            self.simset_simulation(act_map,att_map,output_dir)

        if self.sim_type=="STIR":

            self.stir_simulation(self.params, self.config, act_map,att_map,self.scanner,output_dir)
