#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join, dirname, abspath, isdir, exists
import os, sys
import shutil
import datetime
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

class brainviset(object):

    """
    This class provides iterative viset for brain images.
    You have to initialize the class with a params file.
    The inputs to this class are a PET and a CT from the same patient.
    This class will generate initial maps and call iteratively the simulation class.
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

        print("Welcome to brainviset")

        patient_dir = join(self.dir_data,self.params.get("patient_dirname"))
        pet = join(patient_dir, self.params.get("pet_image"))
        #ct = join(patient_dir, self.params.get("ct_image"))
        mri = join(patient_dir, self.params.get("mri_image"))

        output_name = self.params.get("output_dir")
        output_dir = join(self.dir_results,output_name)
        maps_dir = join(output_dir, "Maps")
        log_file = join(output_dir,'log_sim.log')

        number_of_its = self.params.get("maximumIteration")        
        axialFOV = self.scanner.get("axial_fov")
        
        if not exists(output_dir):
            os.makedirs(output_dir)
        if not exists(maps_dir):
            os.makedirs(maps_dir)

        # We will start generating the initial maps from the PET and the CT
        print("Generating initial act and att maps from PET and CT data...")
        act_map, att_map = tools.petmr2maps(pet, mri, log_file, self.spmrun, maps_dir)

        self.params['att_map'] = att_map

        max_num_it = int(number_of_its)  
        if max_num_it >= 1:
            it=0
            old_corrCoef = 0.0
            new_corrCoef = 0.0
            more_its = True
            while ((it < max_num_it) & more_its):            
                log_file = join(output_dir,"log_sim_It_%s.log" % str(it))
                output_dir_aux = join(output_dir, "It_%s" % str(it))
                components = os.path.split(pet)
                preproc_pet = os.path.join(components[0], 'r' + components[1][0:-3]+"hdr")
    
                self.params['act_map'] = act_map            
                self.params['output_dir'] = output_dir_aux
    
                print("Simulating brain image for iteration %s of %s" % (str(it),number_of_its))
                it_sim = SimPET(self.param_file)
                it_sim.simset_simulation(act_map, att_map, output_dir_aux)
    
                recons_algorithm = self.scanner.get('recons_type')
                recons_it = self.scanner.get('numberOfIterations')
    
                rec_file = join(output_dir_aux, "SimSET_Sim_"+self.params.get("scanner"),recons_algorithm,'rec_%s_%s.hdr' % (recons_algorithm,recons_it))
                
                if exists(rec_file):
                    print("Updating activity map")
                    updated_act_map = join(maps_dir,act_map[0:-5]+"%s.hdr" % str(it+1))
                    tools.update_act_map(self.spmrun, act_map, att_map, preproc_pet, rec_file, updated_act_map, axialFOV, log_file)
                    new_corrCoef = tools.compute_corr_coeff(act_map, updated_act_map, log_file)
                    print("Correlation coefficiente between images is %s " % (new_corrCoef))
                    if ((new_corrCoef>0.99) | (old_corrCoef>new_corrCoef)):
                        print("No further iterations are necessary")
                        print("Final activity map is %s" %(act_map))
                        more_its = False
                    else:
                        print("Not converging yet. Preparing for iteration %s of %s" % ((it+1),number_of_its))
                        it=it+1
                        old_corrCoef = new_corrCoef
                        act_map = updated_act_map
                else:
                    raise Exception('The brainviset process was aborted.')
                    ## Place some logging here
                    sys.exit(1)
                
            if more_its:
                print("Maximum number of iterations reached")
                print("Final activity map is %s" %(updated_act_map))