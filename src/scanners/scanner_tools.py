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

from utils import tools
from utils import resources as rsc

def create_cylindrical_detector(scanner, output):
    
    nrings_z = scanner.Ring_Number
    crystal_z_size = scanner.Ring_Z_thickness
    gap_z_size = scanner.Gap_between_rings
    cyln_inner_radius = scanner.Ring_Inner_Radious
    cyln_outer_radius = scanner.Ring_Outer_Radious
    energy_resolution = scanner.Energy_Resolution_percent
    timing_resolution = scanner.Timing_Resolution_ns
    material = scanner.SimSET_Ring_Material

    nrings_total = 2*nrings_z-1
    axial_lenght = nrings_z*crystal_z_size + (nrings_z-1)*gap_z_size
    z_min = -axial_lenght/2

    print "Number of rings in the scanner is: %s" % nrings_z
    print "Cristal z is: %s cm" % crystal_z_size
    print "Gaps are: %s cm" % gap_z_size
    print "Ring thickness is: %s cm" % (cyln_outer_radius-cyln_inner_radius)
    print "Energy resolution is: %s" % energy_resolution
    print "Timing resolution is: %s" % timing_resolution

    new_file = open(output, "w")
    new_file.write(
        "ENUM detector_type = cylindrical \n\n" +
        "# This detector example has %s axial rings and %s gaps \n" % (nrings_z,nrings_z-1) +
        "INT	cyln_num_rings = %s \n\n" % nrings_total
        )

    for i in range(1,nrings_z+1):

        ring_zmin = z_min + (i-1)*crystal_z_size + (i-1)*gap_z_size
        ring_zmax = ring_zmin + crystal_z_size
        gap_zmax = ring_zmin + crystal_z_size + gap_z_size

        new_file.write(
            "# RING #%s \n" % i +
            "# The following defines the ring parameters \n" +
            "LIST	cyln_ring_info_list = 5 \n" +
            "INT	cyln_num_layers = 1 \n" +
	        "LIST	cyln_layer_info_list = 4 \n" +
	        "BOOL	cyln_layer_is_active = TRUE \n" +
	    	"INT	cyln_layer_material = %s \n" % material +
	    	"REAL	cyln_layer_inner_radius = %s \n" % cyln_inner_radius +
	    	"REAL	cyln_layer_outer_radius = %s \n" % cyln_outer_radius +
	        "REAL	cyln_min_z = %s \n" % ring_zmin +
	        "REAL	cyln_max_z = %s \n\n" % ring_zmax
        )

        if not i==nrings_z:

            new_file.write(
                "# GAP #%s \n" % i +
                "# The following defines the gap parameters \n" +
                "LIST	cyln_ring_info_list = 5 \n" +
                "INT	cyln_num_layers = 1 \n" +
	            "LIST	cyln_layer_info_list = 4 \n" +
	            "BOOL	cyln_layer_is_active = FALSE \n" +
		        "INT	cyln_layer_material = 0 \n" +
		        "REAL	cyln_layer_inner_radius = %s \n" % cyln_inner_radius +
		        "REAL	cyln_layer_outer_radius = %s \n" % cyln_outer_radius +
	            "REAL	cyln_min_z = %s \n" % ring_zmax +
	            "REAL	cyln_max_z = %s \n\n" % gap_zmax
                )

    new_file.write(
        "REAL    reference_energy_keV = 511.0 \n" +
        "REAL    energy_resolution_percentage = %s \n" % energy_resolution + 
        "REAL 	photon_time_fwhm_ns = %s \n" % timing_resolution
        )

    new_file.close()

def create_simplepet_detector(scanner, output):
    
    new_file = open(output, "w")

    energy_resolution = scanner.Energy_Resolution_percent
    
    new_file.write(
        "ENUM detector_type = simple_pet \n\n" +
        "REAL    reference_energy_keV = 511.0 \n" +
        "REAL    energy_resolution_percentage = %s \n" % energy_resolution
        )

    new_file.close()        