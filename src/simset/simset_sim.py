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

        self.act_map = act_map
        self.att_map = att_map
        self.output_dir = projections_dir
        self.center_slice = params.get("center_slice")

        self.sim_dose = params.get("total_dose")
        self.s_photons = params.get("sampling_photons")
        self.photons = params.get("photons")
        self.sim_time = params.get("simulation_time")
        self.divisions = params.get("divisions")
        self.phglistmode = scanner.get("phglistmode")

    def run_simset_simulation(self,sim_dir):
        
        act, act_data = tools.nib_load(self.act_map)
        att, att_data = tools.nib_load(self.att_map)

        # Creates the data files for the simulation maps
        act_img = self.act_map[0:-3] + "img"
        att_img = self.att_map[0:-3] + "img"
        shutil.copy(act_img,join(sim_dir,"act.dat"))
        shutil.copy(att_img,join(sim_dir,"att.dat"))

        # It generates a new act_table for the simulation
        if self.sim_dose !=0:
            phantom_counts = np.sum(act_data) #mCi
            phantom_dose = abs(phantom_counts*act.affine[0,0]*act.affine[1,1]*act.affine[2,2]) #mCi
            act_table_factor = self.sim_dose*1000/phantom_dose
        else:
            act_table_factor = 1

        my_act_table = join(sim_dir,"phg_act_table")
        simset_tools.make_simset_act_table(act_table_factor, my_act_table)

        # If Sampling Photons is 0, importance sampling is deactivated, so we use photons as the input.
        if self.s_photons == 0:
            sim_photons = self.photons/self.divisions
        else:
        # If Sampling Photons is not 0, we make a first simulation for importance sampling
            sim_photons = self.s_photons

        sim_time = self.sim_time/self.divisions
        scanner_radius = self.scanner.get("scanner_radius")

        my_phg_file = join(sim_dir,"phg.rec")

        simset_tools.make_simset_phg(self.config, my_phg_file, sim_dir, 
                                     act, scanner_radius, self.center_slice,
                                     sim_photons, sim_time, 
                                     add_randoms=False, phg_hf=self.phglistmode, S=0)

        my_det_file = join(sim_dir,"det.rec")

        # We activate det_listmode if demanded by user or if add_randoms is on
        if self.params.add_randoms==1 or self.scanner.get("detlistmode")==1:
            det_listmode = 1
        else: 
            det_listmode = 0

        simset_tools.make_simset_cyl_det(self.scanner, my_det_file, sim_dir, det_listmode)

        my_bin_file = join(sim_dir,"bin.rec")
        simset_tools.make_simset_bin(self.config, my_bin_file, self.scanner)
    
    def run(self): 

        processes = []

        for division in range(self.divisions):

            division_dir = join(self.output_dir, "division_" + str(division))
            os.makedirs(division_dir)
            p = Process(target=self.run_simset_simulation, args=(division_dir,))
            processes.append(p)
            p.start()
            time.sleep(5)


        