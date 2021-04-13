#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join, dirname, abspath, isdir, exists
import os, sys
import shutil
import datetime
import yaml

from utils import tools
from utils import wb_tools

class SimPET(object):
    """
    This class provides main SimPET functions.
    You have to initialize the class with a params file.
    Before using SimPET, check out the README.

    """

    def __init__(self,param_file,config_file="config.yml", params = False):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))

        # The following lines will read the general, scanner and config parameters
        if not params:
            with open(param_file, 'rb') as f:
                self.params = yaml.load(f.read(), Loader=yaml.FullLoader)
        else:
            self.params = params

        # This will load the simulation type (SimSET or STIR)
        self.sim_type = self.params.get("sim_type")

        # This will load the scanner params for the selected scanner
        self.scanner_model = self.params.get("scanner")
        scanner_parfile = join(self.simpet_dir,"scanners",self.scanner_model + ".yml")
        with open(scanner_parfile, 'rb') as f:
            self.scanner = yaml.load(f.read(), Loader=yaml.FullLoader)

        # This will load the environment config
        with open(config_file, 'rb') as f:
            self.config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.cesga = self.config.get("cesga")

        if self.cesga:
            self.dir_data =  self.config.get("cesga_data_path")
        else:
            self.dir_data =  self.config.get("dir_data_path")
            if not self.dir_data:
                self.dir_data = join(self.simpet_dir, "Data")

        if self.cesga:
            self.dir_results =  self.config.get("cesga_results_path")
        else:
            self.dir_results =  self.config.get("dir_results_path")
            if not self.dir_results:
                self.dir_results = join(self.simpet_dir, "Results")
        if not exists(self.dir_results):
            os.makedirs(self.dir_results)

    def simset_simulation(self,act_map,att_map,output_dir):

        projections_dir = join(output_dir, "SimSET_Sim_" + self.scanner_model)

        from src.simset import simset_sim as sim

        if self.params.get("do_simulation")==1:

            if exists(projections_dir):
                if self.config.get("interactive_mode")==1:
                    print("The introduced output dir already has a SimSET simulation.Proceeding will delete it.")
                    remove = input(" Write 'Y' to delete it: ")
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

            my_simulation = sim.SimSET_Simulation(self.params,self.config,act_map,att_map,self.scanner,projections_dir)
            my_simulation.run()

        if self.params.get("do_reconstruction")==1:

            reconstruction_type = self.scanner.get("recons_type")

            if not exists (projections_dir):
                    raise Exception('The projections directory does not exist. Run your simulation first.')
                    ## Place some logging here
                    sys.exit(1)

            postprocess_log = join(projections_dir, "postprocessing.log")

            # If it is a new simulation or if the trues.hdr were not added previously, it makes the postprocessing
            if not exists (postprocess_log):
                print("Your simulation SimSET outputs were not processed previously. We will try it now...")
                my_simulation = sim.SimSET_Simulation(self.params,self.config,act_map,att_map, self.scanner,projections_dir)
                my_simulation.simulation_postprocessing()

            reconstruction_dir = join(projections_dir,reconstruction_type)

            if exists(reconstruction_dir):
                if self.config.get("interactive_mode")==1:
                    print("The introduced output dir already has a %s reconstruction.Proceeding will delete it." % reconstruction_type)
                    remove = input(" Write 'Y' to delete it: ")
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

        projections_dir = join(output_dir, "STIR_Sim_" + self.scanner_model)

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
        if not exists(maps_dir):
            os.makedirs(maps_dir)

        log_file = join(output_dir,"logfile.log")

        act_map, att_map = tools.convert_map_values(act_map,att_map,maps_dir,log_file,mode=self.sim_type)

        if self.sim_type=="SimSET":

            self.simset_simulation(act_map,att_map,output_dir)

        if self.sim_type=="STIR":

            self.stir_simulation(self.params, self.config, act_map,att_map,self.scanner,output_dir)

class wholebody_simulation(object):

    """
    This class provides functionalities to simulate several beds.
    You have to initialize the class with a params file. The class will iteratively call the SimPET class.
    Before using SimPET, check out the README.

    """

    def __init__(self,param_file,config_file="config.yml", params = False):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))
        self.param_file = param_file
        self.config_file = config_file

        # The following lines will read the general, scanner and config parameters

        if not params:
            with open(self.param_file, 'rb') as f:
                self.params = yaml.load(f.read(), Loader=yaml.FullLoader)
        else:
            self.params = params

        self.sim_type = self.params.get("sim_type")
        self.zmin = self.params.get("z_min")
        self.zmax = self.params.get("z_max")
        
        # This will load the scanner params for the selected scanner
        self.scanner_model = self.params.get("scanner")
        scanner_parfile = join(self.simpet_dir,"scanners",self.scanner_model + ".yml")
        with open(scanner_parfile, 'rb') as f:
            self.scanner = yaml.load(f.read(), Loader=yaml.FullLoader)

        # This will load the environment config
        with open(config_file, 'rb') as f:
            self.config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.cesga = self.config.get("cesga")

        if self.cesga:
            self.dir_data =  self.config.get("cesga_data_path")
        else:
            self.dir_data =  self.config.get("dir_data_path")
            if not self.dir_data:
                self.dir_data = join(self.simpet_dir, "Data")

        if self.cesga:
            self.dir_results =  self.config.get("cesga_results_path")
        else:
            self.dir_results =  self.config.get("dir_results_path")
            if not self.dir_results:
                self.dir_results = join(self.simpet_dir, "Results")
        if not exists(self.dir_results):
            os.makedirs(self.dir_results)

    def run(self):

        patient_dir = self.params.get("patient_dirname")
        act_map = join(self.dir_data, patient_dir, self.params.get("act_map"))
        att_map = join(self.dir_data, patient_dir, self.params.get("att_map"))
        output_name = self.params.get("output_dir")
        output_dir = join(self.dir_results,output_name)
        maps_dir = join(output_dir,"Maps")

        # THIS WILL POP UP EVEN IF ONLY RECONSTRUCTION IS DONE. MOVE IT OUT
        if not exists(output_dir):
            os.makedirs(output_dir)

        log_file = join(output_dir,"logfile.log")

        beds_cs =  wb_tools.calculate_center_slices(act_map,self.scanner, self.zmin, self.zmax)

        print("The number of beds to simulate is: %s" % len(beds_cs))
        print("Beds center slides: %s" % beds_cs)

        j = 1

        for cs in beds_cs:

            bed_dir = join(output_dir,"Bed_cs_%s" % cs)
            if not exists(bed_dir):
                os.makedirs(bed_dir)
            
            self.params['center_slice'] = cs
            self.params['output_dir'] = output_name + "/Bed_cs_%s" % cs

            print("Simulating bed %s with center slice %s" % (j,cs))

            bed_simu = SimPET(self.param_file,self.config_file, params=self.params)
            bed_simu.run()

        recons_beds = []
        recons_algorithm = self.scanner.get('recons_type')
        recons_it = self.scanner.get('numberOfIterations')

        for cs in beds_cs:

            recons_dir = join(output_dir,"Bed_cs_%s" % cs,"%s_sim_%s" % (self.sim_type,self.scanner_model),recons_algorithm)
            recons_file = join(recons_dir,'rec_%s_%s.hdr' % (recons_algorithm,recons_it))
            recons_beds.append(recons_file)

        joint_beds =join(output_dir,'rec_%s_%s.hdr' % (recons_algorithm,recons_it))
        wb_tools.join_beds_wb(recons_beds,joint_beds)

class wholebody_viset(object):

    """
    This class provides iterative viset for whole-body images.
    You have to initialize the class with a params file.
    The inputs to this class are a PET and a CT from the same patient.
    This class will generate initial maps and call iteratively the wholebody_simulation class.
    The number of iterations is set in the main config file.
    Before using SimPET, check out the README.

    """

    def __init__(self,param_file,config_file="config.yml"):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))
        self.param_file = param_file
        self.config_file = config_file
        

        # The following lines will read the general, scanner and config parameters
        with open(self.param_file, 'rb') as f:
            self.params = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.sim_type = self.params.get("sim_type")
        
        # This will load the scanner params for the selected scanner
        self.scanner_model = self.params.get("scanner")
        scanner_parfile = join(self.simpet_dir,"scanners",self.scanner_model + ".yml")
        with open(scanner_parfile, 'rb') as f:
            self.scanner = yaml.load(f.read(), Loader=yaml.FullLoader)

        # This will load the environment config
        with open(self.config_file, 'rb') as f:
            self.config = yaml.load(f.read(), Loader=yaml.FullLoader)

        spm_path = self.config.get("spm_path")
        matlab_path = self.config.get("matlab_mcr_path")
        self.spmrun = "sh %s/run_spm12.sh %s batch" % (spm_path, matlab_path)

        self.cesga = self.config.get("cesga")

        if self.cesga:
            self.dir_data =  self.config.get("cesga_data_path")
        else:
            self.dir_data =  self.config.get("dir_data_path")
            if not self.dir_data:
                self.dir_data = join(self.simpet_dir, "Data")

        if self.cesga:
            self.dir_results =  self.config.get("cesga_results_path")
        else:
            self.dir_results =  self.config.get("dir_results_path")
            if not self.dir_results:
                self.dir_results = join(self.simpet_dir, "Results")
        if not exists(self.dir_results):
            os.makedirs(self.dir_results)

    def run(self):

        print("Welcome to WB_Viset")

        patient_dir = join(self.dir_data,self.params.get("patient_dirname"))
        pet = join(patient_dir, self.params.get("pet_image"))
        ct = join(patient_dir, self.params.get("ct_image"))

        output_name = self.params.get("output_dir")
        output_dir = join(self.dir_results,output_name)
        log_file = join(output_dir,'log_sim.log')

        number_of_its = self.params.get("viset_iterations")
        

        if not exists(output_dir):
            os.makedirs(output_dir)

        # We will start generating the initial maps from the PET and the CT
        print("Generating initial act and att maps from PET and CT data...")
        generate_maps = wb_tools.wbpetct2maps(self.spmrun, patient_dir, log_file, ct, pet)
        generate_maps.run()

        for it in range(int(number_of_its)):

            act_map = join(patient_dir,"act_simset_it%s.hdr" % str(it))
            att_map = join(patient_dir,"act_simset_it0.hdr")
            
            components = os.path.split(pet)
            preproc_pet = os.path.join(components[0], 'r' + components[1])

            self.params['act_map'] = "act_simset_it%s.hdr" % str(it)
            self.params['att_map'] = "att_simset_it0.hdr"
            self.params['output_dir'] = output_name + "/It_%s" % str(it)

            print("Simulating wholebody image for iteration %s of %s" % (str(it),number_of_its))
            it_sim = wholebody_simulation(self.param_file,config_file=self.config_file, params=self.params)
            it_sim.run()

            recons_algorithm = self.scanner.get('recons_type')
            recons_it = self.scanner.get('numberOfIterations')

            it_output = join(output_dir,"It_%s" % str(it))
            rec_file = join(it_output,'rec_%s_%s.hdr' % (recons_algorithm,recons_it))
            
            if exists(rec_file):
                print("Updating activity map and preparing for iteration %s of %s" % ((it+1),number_of_its))
                updated_act = join(patient_dir,"act_simset_it%s.hdr" % str(it+1))
                wb_tools.update_act_map(self.spmrun, act_map, att_map, preproc_pet, rec_file,updated_act)













