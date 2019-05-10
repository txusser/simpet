#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join,dirname,abspath,isdir
import os
import shutil
import datetime
from utils import resources as rsc
from utils import tools
import config

class SIMPET(object):
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

    def __init__(self,param_file):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))
        self.dir_data = join(self.simpet_dir, "Data")
        self.param_file = param_file
        
        self.simulation_dir = join(self.dir_data,self.simulation_name)
        if not isdir(self.simulation_dir):
            os.makedirs(self.simulation_dir)
        self.patient_dir = join(self.simulation_dir,"Patient")
        if not isdir(self.patient_dir):
            os.makedirs(self.patient_dir)
        self.sim_maps_dir = join(self.simulation_dir,"Maps")
        if not isdir(self.sim_maps_dir):
            os.makedirs(self.sim_maps_dir)
        self.results_dir = join(self.simulation_dir,"Results")
        if not isdir(self.results_dir):
            os.makedirs(self.results_dir)

        self.logfile = join(self.simulation_dir, "Simpet.log")

        #SPM variables
        self.matlab_mcr_path = config.matlab_mcr_path
        self.spm_path = config.spm_path
        self.spm_run = "sh %s/run_spm12.sh %s batch" % (self.spm_path, self.matlab_mcr_path)

    def petmr2maps(self,pet_image,mri_image,mode="STIR"):
        """
        It will create act and att maps from PET and MR images.
        Required inputs are:
        pet_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mri_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mode: Choose STIR or SIMSET. The maps will be different for each simulation.
        The inputs will be stored to Data/simulation_name/Patient as reformatted/corregistered Analyze
        The maps will be stored on Data/simulation_name/Maps
        """
        message = "GENERATING ACT AND ATT MAPS FROM PETMR IMAGES"
        tools.log_message(self.logfile, message, mode='info')

        #First of all lets take all to analyze
        pet_hdr = tools.anything_to_hdr_convert(pet_image)
        pet_hdr = tools.copy_analyze(pet_hdr,image2=False,dest_dir=self.patient_dir)
        pet_hdr = tools.prepare_input_image(pet_hdr,self.logfile,min_voxel_size=1.5)
        pet_img = pet_hdr[0:-3]+"img"

        mri_hdr = tools.anything_to_hdr_convert(mri_image)
        mri_hdr = tools.copy_analyze(mri_hdr,image2=False,dest_dir=self.patient_dir)
        mri_hdr = tools.prepare_input_image(mri_hdr,self.logfile,min_voxel_size=1.5)
        mri_img = mri_hdr[0:-3]+"img"

        #Performing PET/MR coregister
        mfile = os.path.join(self.patient_dir,"fusion.m")
        correg_pet_img = tools.image_fusion(self.spm_run, mfile, mri_img, pet_img, self.logfile)

        #Now the map generation
        from src.patient2maps import patient2maps

        my_map_generation = patient2maps(self.spm_run, self.sim_maps_dir, self.logfile,
                                         mri_img, correg_pet_img, mode=mode)
        activity_map_hdr, attenuation_map_hdr = my_map_generation.run()

        return activity_map_hdr, attenuation_map_hdr

    def conver_map_mode(self,act_map,att_map,mode="SIMSET"):

        message = "CONVERTING ACT AND ATT TO %s" % mode
        tools.log_message(self.logfile, message, mode='info')

        cambia_formato = rsc.get_rsc('change_format', 'fruitcake')
        cambia_val = rsc.get_rsc('change_values', 'fruitcake')

        new_att_map = join(self.sim_maps_dir, "attenuation_map_" + mode +".hdr")
        new_act_map = join(self.sim_maps_dir,"activity_map_" + mode +".hdr")

        if mode == "SIMSET":

            rcommand = '%s %s %s 0.096 1' % (cambia_val, att_map, new_att_map)
            tools.osrun(rcommand, self.logfile)
            rcommand = '%s %s %s 0.135 3 ' % (cambia_val, new_att_map, new_att_map)
            tools.osrun(rcommand, self.logfile)
            rcommand = '%s %s %s 1B' % (cambia_formato, new_att_map, new_att_map)
            tools.osrun(rcommand, self.logfile)
            rcommand = '%s %s %s 1B' % (cambia_formato, new_act_map, new_act_map)
            tools.osrun(rcommand, self.logfile)

        if mode == "STIR":

            rcommand = '%s %s %s fl' % (cambia_formato, att_map, new_att_map)
            tools.osrun(rcommand, self.logfile)
            rcommand = '%s %s %s fl' % (cambia_formato, new_act_map, new_act_map)
            tools.osrun(rcommand, self.logfile)
            rcommand = '%s %s %s 1  0.096' % (cambia_val, new_att_map, new_att_map)
            tools.osrun(rcommand, self.logfile)
            rcommand = '%s %s %s 3  0.135' % (cambia_val, new_att_map, new_att_map)
            tools.osrun(rcommand, self.logfile)

        return new_act_map, new_att_map

    def simset_simulation(self,param_file):

        from src.simset import simset_sim as sim

    def stir_simulation(self,param_file):

        from src.simset import simset_sim as sim


    def run(self,param_file):
        
        import param_file as params

        

        if params.sim_type=="SimSET":
            self.simset_simulation(param_file)

        if params.sim_type=="STIR":
            self.stir_simulation(param_file)

        



        

