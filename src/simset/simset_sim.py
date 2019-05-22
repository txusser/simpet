from os.path import join,dirname,abspath,isdir
import os, sys
import shutil
import datetime, time
from multiprocessing import Process
from utils import resources as rsc
from utils import tools
import yaml
import numpy as np
import simset_tools

class SimSET_Simulation(object):
    """This class provides functions to run a SimSET simulation."""

    def __init__(self,params,config,act_map,att_map,scanner,projections_dir):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))

        self.params = params
        self.config = config
        self.scanner = scanner

        self.simset_dir = self.config.get("dir_simset")

        self.act_map = act_map
        self.att_map = att_map
        self.output_dir = projections_dir
        self.center_slice = params.get("center_slice")

        self.sim_dose = params.get("total_dose")
        self.s_photons = params.get("sampling_photons")
        self.photons = params.get("photons")
        self.sim_time = params.get("simulation_time")
        self.divisions = params.get("divisions")
        
        self.detlistmode = scanner.get("detlistmode")
        self.phglistmode = scanner.get("phglistmode")
        self.add_randoms = params.get("add_randoms")

    def run(self): 

        processes = []

        for division in range(self.divisions):

            division_dir = join(self.output_dir, "division_" + str(division))
            os.makedirs(division_dir)
            p = Process(target=self.run_simset_simulation, args=(division_dir,))
            processes.append(p)
            p.start()
            time.sleep(5)
        
        for process in processes:
            process.join()

    def prepare_simset_files(self, sim_dir, act_table_factor, act, sim_photons, sim_time, sampling):

        log_file = join(sim_dir, "simpet.log")
        # Establishing necessary parameters
        scanner_radius = self.scanner.get("scanner_radius")

        # We activate det_listmode if demanded by user or if add_randoms is on
        if self.add_randoms==1 and self.detlistmode==1:
            det_listmode = 1
            add_randoms = True
        elif self.add_randoms==0 and self.detlistmode==1==1: 
            det_listmode = 1
            add_randoms = False
        else:
            det_listmode = 0
            add_randoms = False

        # Creating the act table for the simulation....
        my_act_table = join(sim_dir,"phg_act_table")
        simset_tools.make_simset_act_table(act_table_factor, my_act_table, log_file=log_file)

        # Creating the phg for the simulation...
        my_phg_file = join(sim_dir,"phg.rec")
        simset_tools.make_simset_phg(self.config, my_phg_file, sim_dir, act, scanner_radius, self.center_slice,
                                     sim_photons, sim_time, add_randoms, self.phglistmode, sampling, log_file=log_file)

        my_det_file = join(sim_dir,"det.rec")
        simset_tools.make_simset_cyl_det(self.scanner, my_det_file, sim_dir, det_listmode, log_file=log_file)

        my_bin_file = join(sim_dir,"bin.rec")
        simset_tools.make_simset_bin(self.config, my_bin_file, sim_dir, self.scanner, add_randoms, log_file=log_file)

        simset_tools.make_index_file(sim_dir, self.simset_dir, log_file=log_file)

        return my_phg_file

    def run_simset_simulation(self,sim_dir):
        
        log_file = join(sim_dir, "simpet.log")

        act, act_data = tools.nib_load(self.act_map) 

        # It generates a new act_table for the simulation
        if self.sim_dose !=0:
            phantom_counts = np.sum(act_data)
            voxel_size = act.affine[0,0]*act.affine[1,1]*act.affine[2,2]/1000
            phantom_dose = abs(phantom_counts*voxel_size) #uCi
            act_table_factor = self.sim_dose*1000/phantom_dose
        else:
            act_table_factor = 1

        # Creates the data files from the simulation maps
        act_img = self.act_map[0:-3] + "img"
        att_img = self.att_map[0:-3] + "img"
        shutil.copy(act_img,join(sim_dir,"act.dat"))
        shutil.copy(att_img,join(sim_dir,"att.dat"))

        # If Sampling Photons is 0, importance sampling is deactivated, so we use photons as the input.
        if self.s_photons == 0 or self.params.get("add_randoms") == 1:
            print("Importance sampling is being deactivated because add_randoms is set to 1")
            if self.photons!=0:
                sim_photons = self.photons/self.divisions
            else:
                sim_photons = self.photons
        else:
            # If Sampling Photons is not 0 and no randoms, we make a first simulation for importance sampling
            sim_photons = self.s_photons

        sim_time = self.sim_time/self.divisions

        my_phg = self.prepare_simset_files(sim_dir, act_table_factor, act, sim_photons, sim_time, 0)
        my_log = join(sim_dir,"simset_s0.log")

        command = "%s/bin/phg %s > %s" % (self.simset_dir, my_phg, my_log)
        tools.osrun(command, log_file)

        if self.s_photons != 0 and self.params.get("add_randoms") != 1:
            if self.photons!=0:
                sim_photons = self.photons/self.divisions
            else:
                sim_photons = self.photons
            
            rec_weight = join(sim_dir,"rec.weight")
            os.remove(rec_weight)
            
            my_phg = self.prepare_simset_files(sim_dir, act_table_factor, act, sim_photons, sim_time, 1)
            my_log = join(sim_dir,"simset_s1.log")
            
            command = "%s/bin/phg %s > %s" % (self.simset_dir, my_phg, my_log)
            tools.osrun(command, log_file)

        simset_tools.process_weights(rec_weight,sim_dir,self.scanner,self.add_randoms)

        if self.add_randoms == 1:

            print ("To be done")

        