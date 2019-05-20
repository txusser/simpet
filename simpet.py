#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join,dirname,abspath,isdir,exists
import os, sys
import shutil
import datetime
from utils import resources as rsc
from utils import tools
import yaml

class SimPET(object):
    """
    This class provides main SimPET functions.
    You have to initialize the class with a simulation_name.

    A directory structure will be created under Data/simulation_name including:
    Data/simulation_name/Patient: If your process starts with PET and MR images, they will be copied here
    Data/simulation_name/Maps: If your process starts with act and att maps, they will be copied here
    Data/simulation_name/Results: Your sim results and brainviset results will be stored here

    This class is meant to work out of the box.
    You need Matlab MCR v901 in order to run this. It is possible that you need to modify the self.matlab_mcr_path.
    MCR Paths working out of the box are:
    /opt/MATLAB/MATLAB_Compiler_Runtime/v901/
    /usr/local/MATLAB/MATLAB_Runtime/v901/
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

        # This will load the scanner params for the selected scanner
        scanner_model = self.params.get("scanner")
        scanner_parfile = join(self.simpet_dir,"scanners",scanner_model + ".yml")
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

        if self.params.get("do_simulation")==1:

            from src.simset import simset_sim as sim

            projections_dir = join(output_dir, "SimSET_Sim")

            if exists(projections_dir) and self.config.get("interactive_mode")==1:
                print("The introduced output dir already has a SimSET simulation.Proceeding will delete it.")
                remove = raw_input(" Write 'Y' to delete it: ")
                print("You can disable this prompt by deactivating interactive mode in the config file.")
                if remove == "Y":
                    shutil.rmtree(projections_dir)
                else:
                    raise Exception('The simulation was aborted.')
                    ## Place some logging here
                    sys.exit(1)

            os.makedirs(projections_dir)
            
            my_simulation = sim.SimSET_Simulation(self.params,self.config,act_map,att_map, self.scanner,projections_dir)
            my_simulation.run()

        if self.params.get("do_reconstruction")==1:

            from src.simset import simset_recons as recons

            reconstruction_dir = join(output_dir, "SimSET_STIR_Recons")

            if not exists(reconstruction_dir):
                os.makedirs(reconstruction_dir)
            
            my_reconstruction = recons.SimSET_Reconstruction(self.params,self.config)
            my_reconstruction.run()

    def stir_simulation(self,param_file):

        from src.simset import simset_sim as sim

    def run_simulation(self):

        from utils import tools
        sim_type = self.params.get("sim_type")

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

        act_map, att_map = tools.convert_map_values(act_map,att_map,maps_dir,log_file,mode=sim_type)
        
        if sim_type=="SimSET":

            self.simset_simulation(act_map,att_map,output_dir)

        if sim_type=="STIR":

            self.stir_simulation(self.params, self.config, act_map,att_map,self.scanner,output_dir)

        

        

        

        
            

            




        

        



        

