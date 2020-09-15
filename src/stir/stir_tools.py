#!/usr/bin/env python2.7 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
import os
from os.path import join, exists, isdir, dirname, basename, split
import shutil
from multiprocessing import Process
import nibabel as nib
import numpy as np
import yaml

from utils import tools
from utils import resources as rsc

def create_stir_hs_from_detparams(params,output_file, output_format="SimSET"):

    num_rings = params.get("num_rings")
    max_z = params.get("axial_fov")/2
    min_z = -params.get("axial_fov")/2
    z_crystal_size = params.get("z_crystal_size")
    gap_size = (max_z-min_z-z_crystal_size*num_rings)/(num_rings-1)
    ring_spacing = z_crystal_size + gap_size

    min_td = -params.get("scanner_radius")
    max_td = params.get("scanner_radius")
    td_bins = params.get("num_td_bins")
    bin_size = (max_td-min_td)/float(td_bins)
    matrix_size, ring_difference = generate_segments_lists_stir(num_rings, num_rings-1)

    if output_format=="SimSET":
        views_coordinate = 2
        axial_coordinate = 3
    else:
        views_coordinate = 3
        axial_coordinate = 2

    new_file = open(output_file, "w")

    new_file.write(
        "!INTERFILE  :=\n" + 
        "!imaging modality := PT\n" +
        "name of data file := " + output_file[0:-2] + "s" + "\n" +
        "originating system := " + params.get("scanner_name") + "\n" +
        "!version of keys := STIR3.0\n" +
        "!GENERAL DATA :=\n" +
        "!GENERAL IMAGE DATA :=\n" +
        "!type of data := PET\n" +
        "imagedata byte order := LITTLEENDIAN\n" +
        "!PET STUDY (General) :=\n" +
        "!PET data type := Emission\n" +
        "!applied corrections := \n" +
        "!number format := float\n" +
        "!number of bytes per pixel := 4\n" +
        "number of dimensions := 4\n" +
        "matrix axis label [4] := segment\n" +
        "!matrix size [4] := " + str(2*(num_rings-1)+1) + "\n" +
        "matrix axis label [" + str(views_coordinate) +"] := view\n" +
        "!matrix size [" + str(views_coordinate) +"] := " + str(params.get("num_aa_bins")) + "\n" +
        "matrix axis label ["+ str(axial_coordinate) +"] := axial coordinate\n" +
        "!matrix size [" + str(axial_coordinate) + "] := " + matrix_size + "\n" +
        "matrix axis label [1] := tangential coordinate\n" +
        "!matrix size [1] := " + str(td_bins) + "\n" 
        "minimum ring difference per segment := " + ring_difference + "\n" +
        "maximum ring difference per segment := " + ring_difference + "\n" +
        "Scanner parameters:= \n" +
        "Scanner type := " + params.get("scanner_name") + "\n" +
        "Number of rings := " + str(num_rings) + "\n" +
        "Number of detectors per ring := " + str(params.get("num_aa_bins")*2) + "\n" 
        "Inner ring diameter (cm) := " + str(params.get("scanner_radius")*2) + "\n" +
        "Average depth of interaction (cm) := " + str(params.get("average_doi")) + "\n" +
        "Distance between rings (cm) := " + str(ring_spacing) + "\n" +
        "Default bin size (cm) := " + str(bin_size) + "\n" +
        "View offset (degrees) := 0\n" +
        "Maximum number of non-arc-corrected bins := " + str(td_bins) + "\n" +
        "Default number of arc-corrected bins := " + str(td_bins) + "\n" +
        "Energy_resolution := " + str(params.get("energy_resolution")*5.11) + "\n" +
        "Reference energy (in keV) := 511\n" +
        "Number of blocks per bucket in transaxial direction := 1\n" +
        "Number of blocks per bucket in axial direction := 1\n" +
        "Number of crystals per block in axial direction := 1\n" +
        "Number of crystals per block in transaxial direction := 1\n" +
        "Number of crystals per singles unit in axial direction := 1\n" +
        "Number of crystals per singles unit in transaxial direction := 1\n" +
        "end scanner parameters:=\n" +
        "effective central bin size (cm) := " + str(bin_size) + "\n" +
        "number of time frames := 1\n" +
        "start vertical bed position (mm) := 0\n" +
        "start horizontal bed position (mm) := 0\n" +
        "!END OF INTERFILE :=\n"
        )
        
def generate_segments_lists_stir(nrings, max_segment):

    last_segment_sinograms = nrings-max_segment
    my_matrix_size = " "
    my_matrix_ring_difference = " "
    for i in range(last_segment_sinograms, nrings):
        my_matrix_size = my_matrix_size + str(i) + ","
        my_matrix_ring_difference = my_matrix_ring_difference + str(i-nrings) + ","
    for i in range(nrings, last_segment_sinograms-1,-1):
        my_matrix_size = my_matrix_size + str(i) + ","
        my_matrix_ring_difference = my_matrix_ring_difference + str(nrings-i) + ","

    my_matrix_size = "{" + my_matrix_size [0:-1] + "}"
    my_matrix_ring_difference = "{" + my_matrix_ring_difference [0:-1] + "}"

    return my_matrix_size, my_matrix_ring_difference


def create_stir_parfile(scannerParams, recons_algorithm, output_dir):
    
    att_img_stir = join(output_dir,"stir_att.hs")
    max_segment = scannerParams.get("max_segment")
    zoom = scannerParams.get("zoomFactor")
    xyOutputSize = scannerParams.get("xyOutputSize")
    zOutputSize =scannerParams.get("zOutputSize")
    numberOfSubsets = scannerParams.get("numberOfSubsets")
    numberOfIterations = scannerParams.get("numberOfIterations")
    savingInterval = scannerParams.get("savingInterval")
    
    if scannerParams.get("analytical_att_correction") == 1:
        sinogram_stir = join(output_dir,"catt_sinogram.hs")
        additive_sino_stir = join(output_dir, "my_catt_additivesino.hs")
        att_corr_str = ""
    else:
        sinogram_stir = join(output_dir,"stir_sinogram.hs")
        additive_sino_stir = join(output_dir, "stir_additivesino.hs")
        att_corr_str = (
        "Bin Normalisation type := From ProjData \n" + 
        "Bin Normalisation From ProjData := \n" +
        "normalisation projdata filename:= "+att_img_stir + "\n"+
        "End Bin Normalisation From ProjData:= \n")        
                        
    if scannerParams.get("stir_scatt_corr_smoothing") ==1:# Will use smoothed SimSET scatter as additive_sinogram.
        scatt_corr_str = ("additive sinogram := " + additive_sino_stir + "\n\n")
    else:
        scatt_corr_str = ""    
    
    new_file = open(join(output_dir,"Params.par"), "w")
    
    if recons_algorithm == 0: #OSEM
        recFileName = join(output_dir,"rec_OSEM3D")
        new_file.write(
            "OSMAPOSLParameters  :=\n\n" + 
            "objective function type := PoissonLogLikelihoodWithLinearModelForMeanAndProjData\n" +
            "PoissonLogLikelihoodWithLinearModelForMeanAndProjData Parameters := \n\n" +
            "input file := " + sinogram_stir + "\n" +
            "maximum absolute segment number to process := " + str(max_segment)+ "\n" +
            "zero end planes of segment 0 := 0 \n" +
            "sensitivity filename := sens.v \n" +
            "recompute sensitivity := 1 \n" +
            "use subset sensitivities := 0 \n\n" +
            "projector pair type := Matrix \n" +
            " Projector Pair Using Matrix Parameters := \n" +
            " Matrix type := Ray Tracing \n" +
            " Ray tracing matrix parameters := \n" +
            " number of rays in tangential direction to trace for each bin:= 5 \n" +
            " End Ray tracing matrix parameters := \n" +
            " End Projector Pair Using Matrix Parameters := \n\n" +
            att_corr_str +
            "prior type := FilterRootPrior \n" +
            "FilterRootPrior Parameters := \n" +
            " penalisation factor := 0. \n" +
            "  Filter type := Median \n" +
            "   Median Filter Parameters := \n" +
            "   mask radius x := 1 \n" +
            "   mask radius y := 1 \n" +
            "   mask radius z := 1 \n" +
            "   End Median Filter Parameters:= \n" +
            "END FilterRootPrior Parameters := \n\n" +
            scatt_corr_str +
            "zoom := " + str(zoom) + "\n" +
            "xy output image size (in pixels) := " + str(xyOutputSize) + "\n" 
            "Z output image size (in pixels) := " + str(zOutputSize) + "\n\n" +
            "end PoissonLogLikelihoodWithLinearModelForMeanAndProjData Parameters := \n\n" +
            "number of subsets := " + str(numberOfSubsets) + "\n" +
            "number of subiterations := " + str(numberOfIterations) + "\n" +
            "save estimates at subiteration intervals := " + str(savingInterval) + "\n\n" +
            "enforce initial positivity condition:=0 \n\n" +
            "output filename prefix := " + recFileName + "\n\n" +
            "END := \n" 
            )
    elif recons_algorithm == 1: #FBP3D
            
    else: #FBP2D
            
    