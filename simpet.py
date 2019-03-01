#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join,dirname,abspath,isdir
import os
import shutil
import datetime
from utils import resources as rsc
from utils import apple as ap
from utils import spm_tools as spm


class SIMPET(object):
    """
    This class provides main SimPET functions. You have to initialize the class with a simulation_name.
    A directory structure will be created under Data/simulation_name including:
    Data/simulation_name/Patient: If your process starts with PET and MR images, they will be copied here
    Data/simulation_name/Maps: If your process starts with act and att maps, they will be copied here
    Data/simulation_name/Results: Your sim results and brainviset results will be stored here
    
    This class is meant to work out of the box. It is possible that you need to modify the self.matlab_mcr_path.
    """

    def __init__(self,simulation_name):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))
        self.dir_data = join(self.simpet_dir, "Data")
        self.simulation_dir = join(self.dir_data,simulation_name)
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

        #SPM variables
        self.spm_path = join(self.simpet_dir, "include", "spm12")
        self.matlab_mcr_path = "/opt/MATLAB/MATLAB_Compiler_Runtime/v901/"
        if not isdir(self.matlab_mcr_path):
            self.matlab_mcr_path = "/usr/local/MATLAB/MATLAB_Runtime/v901/"
        self.spm_run = "sh %s/run_spm12.sh %s batch" % (self.spm_path, self.matlab_mcr_path)

    def create_sim_maps_from_petmr(self,pet_image,mri_image,mode="STIR"):
        """
        This function will call a class named PET_to_maps on the src directory. 
        It will create act and att maps from PET and MR images.
        Required inputs are:
        pet_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mri_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mode: Choose STIR or SIMSET. The maps will be different for each simulation.
        The inputs will be stored to Data/simulation_name/Patient as reformatted/corregistered Analyze
        The maps will be stored on Data/simulation_name/Maps
        """

        logfile = join(self.simulation_dir, "SimMap_Generation.log")
        
        #First of all lets take all to analyze
        pet_hdr = ap.anything_to_hdr_convert(pet_image)
        pet_hdr = ap.copy_analyze(pet_hdr,image2=False,dest_dir=self.patient_dir)
        pet_hdr = ap.prepare_input_image(pet_hdr,logfile,min_voxel_size=1.5)
        pet_img = pet_hdr[0:-3]+"img"

        mri_hdr = ap.anything_to_hdr_convert(mri_image)
        mri_hdr = ap.copy_analyze(mri_hdr,image2=False,dest_dir=self.patient_dir)
        mri_hdr = ap.prepare_input_image(mri_hdr,logfile,min_voxel_size=1.5)
        mri_img = mri_hdr[0:-3]+"img"

        #Performing PET/MR coregister
        mfile = os.path.join(self.patient_dir,"fusion.m")
        correg_pet_img = spm.image_fusion(self.spm_run, mfile, mri_img, pet_img, logfile)

        #Now the map generation
        from src.PETMR_to_maps import PETMR_to_maps

        my_map_generation = PETMR_to_maps(self.spm_run, self.sim_maps_dir, logfile, mri_img, correg_pet_img, logfile, mode=mode)
        activity_map_hdr, attenuation_map_hdr = my_map_generation.run()

        return activity_map_hdr, attenuation_map_hdr





   

