#!/usr/bin/env python2.7 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
import datetime
import os
from os.path import join, exists, isdir, dirname, basename, split
import shutil
from multiprocessing import Process
import pandas as pd
import nibabel as nib
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter

from utils import tools
from utils import resources as rsc

change_format = rsc.get_rsc('change_format', 'fruitcake')

class wbpetct2maps(object):
    """
    This class will create activity and attenuation maps from PET and CT images.
    Inputs are:
    spm_run: Command to run SPM (i.e. ../run_spm12.sh pathto/mcr/v901)
    maps_path: path where the maps will be stored
    log: logging file
    mri_path: .img of analyze file for mri
    pet_path: .img of analyze file for pet
    mode: STIR or SIMSET
    """

    def __init__(self, spm_run, maps_path, log, ct_path, pet_path, mode):

        # Maps Paths
        self.analysis_path = dirname(pet_path)
        self.maps_path = maps_path
        self.ct_img = ct_path
        self.pet_img = pet_path
        self.mode = mode
        # SPM
        self.spm_run = spm_run
        #Logging
        self.log_file = log

        self.act_smooth_value = 4
        self.nbins_act = 64
        self.log = log

    def run(self):
            
        self.ct_bilinear_hounsfield()
        self.pet_to_actmap()

        # p1.start()
        # p2.start()
        # p1.join()
        # p2.join()

        #act_map, att_map = self.atlas_generation()
        
        #self.cleanup()

        #return act_map, att_map

    def ct_bilinear_hounsfield(self):
        """
        Transforms a CT (Hounsfield Units) into an attenuation map using the bilinear formula
        This method is an approximation used by the GE Discovery
        """
        # Starts login
        message = 'I am generating an attenuation map....'
        print(message)

        u_PET_water = 0.096
        u_PET_bone = 0.172
        u_CT_water = 0.184
        u_CT_bone = 0.428

        ct_image = nib.load(self.ct_img)
        ct_data = ct_image.get_fdata()
        print (ct_data.shape)

        ct_data = median_filter(ct_data, 4)
        att_data = ct_data
        
        indx = np.where((-200<ct_data) & (ct_data<=0))
        att_data[indx] = (u_PET_water*(ct_data[indx]+1000))/1000
        indx = np.where(ct_data>0)
        att_data[indx] = u_PET_water + ct_data[indx]*(u_CT_water/1000)*((u_PET_bone-u_PET_water)/(u_CT_bone-u_CT_water))
        indx = np.where(ct_data<=-200)
        att_data[indx] = 0

        ctmax = np.amax(att_data)

        bins = np.linspace(0.09, 0.105, self.nbins_act)
        binned_ct_data = np.digitize(att_data,bins=bins)

        att_out = join(self.maps_path,'att_binned.hdr')
        att_img = nib.AnalyzeImage(binned_ct_data, ct_image.affine, ct_image.header)
        nib.save(att_img,att_out)

        att_map = np.zeros_like(binned_ct_data)

        # Translation of CT mask to SimSET indices
        # Fat
        indx = np.where(binned_ct_data==26)
        att_map[indx] = 23
        # Soft tissue
        indx = np.where((binned_ct_data>26) & (binned_ct_data<=32))
        att_map[indx] = 23
        # Hard tissue and muscle
        indx = np.where((binned_ct_data>32) & (binned_ct_data<=43))
        att_map[indx] = 7
        # Bone
        indx = np.where(binned_ct_data>43)
        att_map[indx] = 3

        att_out = join(self.maps_path,'att_segment.hdr')
        att_img = nib.AnalyzeImage(att_map, ct_image.affine, ct_image.header)
        nib.save(att_img,att_out)

        att_simset = join(self.maps_path,'att_simset.hdr')

        rcommand = '%s %s %s 1B >> %s' % (change_format, att_out, att_simset, self.log)
        tools.osrun(rcommand,self.log)

    def pet_to_actmap(self):
        """
        Transforms (sort of) a PET image into an activity map. 
        """
        # Starts login
        message = 'I am generating an activity map....'
        print(message)

        pet_image = nib.load(self.pet_img)
        pet_data = pet_image.get_fdata()

        pet_data = median_filter(pet_data, 6)

        pet_out = join(self.maps_path,'pet_denoised.hdr')
        act_img = nib.AnalyzeImage(pet_data, pet_image.affine, pet_image.header)
        nib.save(act_img,pet_out)

        att_out_binned = join(self.maps_path,'att_binned.hdr')
        ct_image = nib.load(att_out_binned)
        ct_data = ct_image.get_fdata()

        act_map_1 = np.zeros_like(ct_data)
        
        for i in range(1,self.nbins_act+1):

            indx = np.where(ct_data==i)
            mean_pet = np.average(pet_data[indx])
            act_map_1[indx] = mean_pet

        att_segment = join(self.maps_path,'att_segment.hdr')
        ct_image = nib.load(att_segment)
        ct_data = ct_image.get_fdata()

        act_map_2 = np.zeros_like(ct_data)
        
        for i in range(23,7,3):

            indx = np.where(ct_data==i)
            mean_pet = np.average(pet_data[indx])
            act_map_2[indx] = mean_pet

        indx = np.where((act_map_1!=0) & (pet_data!=0))

        act_map = np.zeros_like(ct_data)

        act_map[indx] = (act_map_1[indx]+act_map_2[indx]+pet_data[indx])/3

        act_map = gaussian_filter(act_map, 1)

        act_max = np.amax(act_map)

        bins = np.linspace(0.01*act_max, 0.40*act_max, 127)
        binned_act = np.digitize(act_map,bins=bins)

        act_out = join(self.maps_path,'act.hdr')
        act_img = nib.AnalyzeImage(act_map, pet_image.affine, pet_image.header)
        nib.save(act_img,act_out)

        act_out = join(self.maps_path,'act_simset.hdr')
        act_img = nib.AnalyzeImage(binned_act, pet_image.affine, pet_image.header)
        nib.save(act_img,act_out)

        rcommand = '%s %s %s 1B >> %s' % (change_format, act_out, act_out, self.log)
        tools.osrun(rcommand,self.log)


