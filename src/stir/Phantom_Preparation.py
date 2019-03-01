#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import commands
import sys
import shutil
from utils import apple
from utils import spm_tools as spm

class Phantom_Preparation(object):

    def __init__(self, spm_run, act_map, att_map, scanner, scanner_target_size, pet_image=False):

        self.emiss_hdr = act_map
        self.att_hdr = att_map
        self.original_pet = pet_image
        self.target_size = scanner_target_size
        self.scanner = scanner

        self.phantom_dir = os.path.dirname(self.emiss_hdr)
        self.spm_run = spm_run
        self.logfile = os.path.join(self.phantom_dir, "Phantom_Preparation.log")

    def run(self):

        print("Preparing phantoms for the simulation...")
        self.phantom_preparation()

        return self.emiss_hdr, self.att_hdr

    def phantom_preparation(self):

        """
        Generates .hv and .v files from Analyze images and fits the size to the scanner
        """

        for i in [self.emiss_hdr, self.att_hdr, self.original_pet]:
            if i:
                rcommand = "cambia_formato_hdr %s %s fl " % (i,i)
                apple.osrun(rcommand,self.logfile)
                
        zpix, zsize, xpix, xsize, ypix, ysize = apple.read_analyze_header(self.emiss_hdr,self.logfile)

        new_x_dims = int(xsize*xpix/self.target_size[0])
        new_y_dims = int(ysize*ypix/self.target_size[1])
        new_z_dims = int(zsize*zpix/self.target_size[2])

        for i in [self.emiss_hdr, self.att_hdr, self.original_pet]:
            if i:
                output_i = i[0:-4]+"_" + self.scanner + ".hdr"
                rcommand = 'cambia_matriz_imagen_hdr %s %s %s %s %s novecino' % (i, output_i, new_x_dims, new_y_dims, new_z_dims)
                apple.osrun(rcommand,self.logfile)

                rcommand = 'gen_hdr %s %s %s %s fl %s %s %s 0' % (output_i[0:-4], new_x_dims, new_y_dims, new_z_dims,
                            self.target_size[0], self.target_size[1], self.target_size[2])
                apple.osrun(rcommand,self.logfile)

                if i == self.emiss_hdr:
                    # If the input is the activity map it applies positron range and non-colinearity
                    output_img = output_i[0:-3] + "img"
                    mfile = os.path.join(self.phantom_dir, "smooth.m")
                    smoothed = spm.smoothing_xyz(self.spm_run,mfile,output_i,2,2,2,"s",self.logfile)
                    shutil.move(smoothed,output_img)

                if i == self.att_hdr:
                    # If the input is the attenuation map it removes higher values
                    rcommand = "cambia_valores_de_un_intervalo %s %s 1 10000000000000 1 " % (output_i,output_i)
                    apple.osrun(rcommand,self.logfile)

                shutil.copy(output_i[0:-3] + "img", output_i[0:-3] + "v")

                apple.write_interfile_header(output_i[0:-3] + "hv", new_x_dims, self.target_size[0],
                                             new_y_dims, self.target_size[1],new_z_dims, self.target_size[2])

        self.emiss_hdr = self.emiss_hdr[0:-4]+"_" + self.scanner + ".hv"
        self.att_hdr = self.att_hdr[0:-4]+"_" + self.scanner + ".hv"