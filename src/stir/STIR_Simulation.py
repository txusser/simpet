#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import commands
import sys
import shutil
from utils import apple
from utils import spm_tools as spm

class STIR_Simulation(object):

    def __init__(self, stir_dir, scanner_template, proyector, act_map, att_map,results_dir,scanner_target_size, pet_image=False):

        self.emiss_hdr = act_map
        self.att_hdr = att_map
        self.original_pet = pet_image
        self.target_size = scanner_target_size
        self.scanner_template = scanner_template
        self.proyector = proyector

        self.phantom_dir = os.path.dirname(self.emiss_hdr)
        self.results_dir = results_dir
        self.stir_dir = stir_dir

        self.logfile = os.path.join(self.results_dir, "STIR_simulation.log")

    def run(self):

        print("Obtaining emission and attenuation projections...")
        self.create_line_integrals()


    def create_line_integrals(self):
        """
        Uses forward_project to project the activity sinograms!
        """
        rcommand = '%s/forward_project %s/my_line_integrals.hs %s %s %s' % (
                    self.stir_dir, self.results_dir, self.emiss_hdr,self.scanner_template, self.proyector)
        apple.osrun(rcommand,self.logfile)
        

