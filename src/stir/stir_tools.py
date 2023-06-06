#!/usr/bin/env python2.7 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
import os
from os.path import join, dirname
import shutil
import random

from utils import tools
from utils import resources as rsc

def create_stir_hs_from_detparams(scannerParams,output_file, output_format="SimSET"):

    num_rings = scannerParams.get("num_rings")
    max_z = scannerParams.get("axial_fov")/2
    min_z = -scannerParams.get("axial_fov")/2
    z_crystal_size = scannerParams.get("z_crystal_size")
    gap_size = (max_z-min_z-z_crystal_size*num_rings)/(num_rings-1)
    ring_spacing = z_crystal_size + gap_size

    min_td = -scannerParams.get("scanner_radius")
    max_td = scannerParams.get("scanner_radius")
    td_bins = scannerParams.get("num_td_bins")
    bin_size = (max_td-min_td)/float(td_bins)
    matrix_size, ring_difference = generate_segments_lists_stir(num_rings, num_rings-1)

    scanner_name = scannerParams.get("scanner_name")
        
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
        "originating system := " + scanner_name + "\n" +
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
        "!matrix size [" + str(views_coordinate) +"] := " + str(scannerParams.get("num_aa_bins")) + "\n" +
        "matrix axis label ["+ str(axial_coordinate) +"] := axial coordinate\n" +
        "!matrix size [" + str(axial_coordinate) + "] := " + matrix_size + "\n" +
        "matrix axis label [1] := tangential coordinate\n" +
        "!matrix size [1] := " + str(td_bins) + "\n" 
        "minimum ring difference per segment := " + ring_difference + "\n" +
        "maximum ring difference per segment := " + ring_difference + "\n" +
        "Scanner parameters:= \n" +
        "Scanner type := " + scanner_name + "\n" +
        "Number of rings := " + str(num_rings) + "\n" +
        "Number of detectors per ring := " + str(scannerParams.get("num_aa_bins")*2) + "\n" 
        "Inner ring diameter (cm) := " + str(scannerParams.get("scanner_radius")*2) + "\n" +
        "Average depth of interaction (cm) := " + str(scannerParams.get("average_doi")) + "\n" +
        "Distance between rings (cm) := " + str(ring_spacing) + "\n" +
        "Default bin size (cm) := " + str(bin_size) + "\n" +
        "View offset (degrees) := 0\n" +
        "Maximum number of non-arc-corrected bins := " + str(td_bins) + "\n" +
        "Default number of arc-corrected bins := " + str(td_bins) + "\n" +
        "Energy_resolution := " + str(scannerParams.get("energy_resolution")*5.11) + "\n" +
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

def apply_psf(scannerParams, sinogram_stir, log_file):

    num_z_bins = scannerParams.get('num_rings')
    num_aa_bins = scannerParams.get('num_aa_bins')
    num_td_bins = scannerParams.get('num_td_bins')
    psf_value = scannerParams.get('psf_value')

    conv_sino2proy = rsc.get_rsc('conv_sino2proy','fruitcake')
    conv_proy2sino = rsc.get_rsc('conv_proy2sino','fruitcake')
    gen_hdr = rsc.get_rsc('gen_hdr','fruitcake')
    convolution_hdr = rsc.get_rsc('convolucion_hdr','fruitcake')
    
    cortes = num_z_bins * num_z_bins

    projections = join(dirname(sinogram_stir), "projections.hdr")
    
    command = "%s %s fl %s %s %s %s fl" % (conv_sino2proy, sinogram_stir[0:-3] + 's', num_aa_bins, num_td_bins, cortes, projections[0:-3] + 'img')
    tools.osrun(command,log_file)
    
    command = "%s %s %s %s %s fl 1 1 1 0" % (gen_hdr, projections[0:-4], num_td_bins, cortes, num_aa_bins)
    tools.osrun(command,log_file)
    
    conv_projections = join(dirname(sinogram_stir), "conv_projections.hdr")
    command = "%s %s %s %s 2d" % (convolution_hdr, projections, conv_projections,psf_value)
    tools.osrun(command,log_file)

    command = "%s %s fl %s %s %s %s fl" % (conv_proy2sino, conv_projections[0:-3] + 'img', num_aa_bins, num_td_bins, cortes, sinogram_stir[0:-3] + 's')
    tools.osrun(command,log_file)
            
    os.remove(projections)
    os.remove(projections[0:-3]+"img")
    os.remove(conv_projections)
    os.remove(conv_projections[0:-3]+"img")

def add_noise(config, scannerParams, sinogram_stir, log_file):

    stir_dir = config.get("dir_stir")
    poison_noise = join(stir_dir,'bin','poisson_noise')

    noisy_sinogram_stir_path = join(dirname(sinogram_stir),"noisy_stir_sinogram.hs")
    command = "%s -p %s %s %s %s" % (poison_noise, noisy_sinogram_stir_path, sinogram_stir[0:-3] + 'hs', scannerParams.get('add_noise'), random.randint(1,200000))
    tools.osrun(command,log_file)

    create_stir_hs_from_detparams(scannerParams,sinogram_stir[0:-3] + 'hs',"after_poiSson_noise")
    shutil.copy(noisy_sinogram_stir_path[0:-2] + 's', sinogram_stir[0:-3] + 's')
            
    os.remove(noisy_sinogram_stir_path)
    os.remove(noisy_sinogram_stir_path[0:-2]+"s")

def FBP2D_recons(config,scannerParams, sinograms_stir, output_dir, log_file):

    stir_dir = config.get("dir_stir")
    recons = join(stir_dir,'bin','FBP2D')
    
    zoom = scannerParams.get("zoomFactor")
    xyOutputSize = scannerParams.get("xyOutputSize")

    recFileName = join(output_dir,"rec_FBP2D")

    paramsFile = join(output_dir,"FBP2D.par")
    new_file = open(paramsFile, "w")
    new_file.write(
            "fbp2dparameters :=  :=\n\n" + 
            "input file := " + sinograms_stir + "\n" +
            "output filename prefix := " + recFileName + "\n\n" +
            "zoom := " + str(zoom) + "\n" +
            "xy output image size (in pixels) := " + str(xyOutputSize) + "\n\n" 
            "num segments to combine with ssrb := -1 \n\n" +
            "alpha parameter for ramp filter := 1 \n" +
            "cut-off for ramp filter (in cycles) := 0.5 \n\n" +
            "end := \n"
            )

    new_file.close()

    command = '%s %s >> %s' % (recons, paramsFile, log_file)
    tools.osrun(command, log_file)        
            
    output = recFileName + ".hv"
    output = tools.anything_to_hdr_convert(output, log_file)

    return output

def FBP3D_recons(config,scannerParams, sinograms_stir, output_dir, log_file):

    stir_dir = config.get("dir_stir")
    recons = join(stir_dir,'bin','FBP3DRP')
    
    zoom = scannerParams.get("zoomFactor")
    xyOutputSize = scannerParams.get("xyOutputSize")

    recFileName = join(output_dir,"rec_FBP3D")

    paramsFile = join(output_dir,"FBP3D.par")
    new_file = open(paramsFile, "w")
    new_file.write(
            "fbp3drpparameters  :=\n\n" + 
            "input file := " + sinograms_stir + "\n" +
            "output filename prefix := " + recFileName + "\n\n" +
            "zoom := " + str(zoom) + "\n" +
            "xy output image size (in pixels) := " + str(xyOutputSize) + "\n\n" 
            "maximum absolute segment number to process := 2 \n" +
            "num segments to combine with ssrb := -1 \n\n" +
            "alpha parameter for ramp filter := 1 \n" +
            "cut-off for ramp filter (in cycles) := 0.5 \n\n" +
            "alpha parameter for colsher filter in axial direction := 1 \n" +
            "cut-off for colsher filter in axial direction (in cycles) := 0.5 \n" +
            "alpha parameter for colsher filter in planar direction := 1 \n" +
            "cut-off for colsher filter in planar direction (in cycles) := 0.5 \n\n" +
            "stretch factor for colsher filter definition in axial direction := 2 \n" +
            "stretch factor for colsher filter definition in planar direction := 2 \n\n" +
            "transaxial extension for fft := 1 \n" +
            "axial extension for fft := 1 \n\n" +
            "save intermediate images := 0 \n" +
            "display level := 0 \n\n" +
            "end := \n"  
            )

    new_file.close()

    command = '%s %s >> %s' % (recons, paramsFile, log_file)
    tools.osrun(command, log_file)        
            
    output = recFileName + ".hv"
    output = tools.anything_to_hdr_convert((output))

    return output

def FORE_rebin(config, sinograms_stir, maxSegment, output_dir, log_file):
    
    stir_dir = config.get("dir_stir")
    rebin = join(stir_dir,'bin','rebin_projdata')
    paramsFile = join(output_dir,"fore.par")
    sinoFileName = join(output_dir,"fore_sinograms") 
    new_file = open(paramsFile, "w")
      
    new_file.write(
            "Rebin projdata Parameters  := \n" + 
            " rebinning type := FORE \n" +
            "  FORE Parameters := \n" +
            "   input file := " + sinograms_stir + "\n" +
            "   output filename prefix := " + sinoFileName + "\n" +
            "   Smallest angular frequency := 20 \n" +
            "   Smallest transaxial frequency := 20 \n" +
            "   Index for consistency := 20 \n" +
            "   Delta max for small omega := 10 \n\n" +
            "   maximum absolute segment number to process := " +str(maxSegment)+ "\n" +
            "   FORE debug level := 0 \n" +
            "  End FORE Parameters :=  \n" +
            "END := \n" 
            )

    new_file.close()

    command = '%s %s >> %s' % (rebin, paramsFile, log_file)
    tools.osrun(command, log_file) 
    
    return sinoFileName+".hs"

def OSEM2D_recons(config, scannerParams, sinograms_stir, additive_sino_stir, att_stir, output_dir, log_file):
        
    stir_dir = config.get("dir_stir")
    recons = join(stir_dir,'bin','OSMAPOSL')

    #max_segment = scannerParams.get("max_segment")
    maxSegment = scannerParams.get("num_rings") - 1
    sinoFileName = FORE_rebin(config, sinograms_stir, maxSegment, output_dir, log_file)
    
    zoom = scannerParams.get("zoomFactor")
    xyOutputSize = scannerParams.get("xyOutputSize")
    zOutputSize =scannerParams.get("zOutputSize")
    numberOfSubsets = scannerParams.get("numberOfSubsets")
    numberOfIterations = scannerParams.get("numberOfIterations")
    savingInterval = scannerParams.get("savingInterval")
    
    scan_radius = scannerParams.get("scanner_radius")
    td_bins = scannerParams.get("num_td_bins")
    bin_size = (2*scan_radius)/float(td_bins)
    xyVoxelSize = round(10*(bin_size/zoom),2) #in mm
    zoom_aux=1
    xyOutputSize_aux=round(xyOutputSize/zoom)

    if scannerParams.get("analytical_att_correction") == 1:
        att_corr_str = ""
    elif scannerParams.get("stir_recons_att_corr")==1:
        att_corr_str = (
        "Bin Normalisation type := From ProjData \n" + 
        "Bin Normalisation From ProjData := \n" +
        "normalisation projdata filename:= "+att_stir + "\n"+
        "End Bin Normalisation From ProjData:= \n")        
                        
    if scannerParams.get("stir_scatt_corr_smoothing") ==1:# Will use smoothed SimSET scatter as additive_sinogram.
        scatt_corr_str = ("additive sinogram := " + additive_sino_stir + "\n\n")
    else:
        scatt_corr_str = ""
        
    if scannerParams.get("inter_iteration_filter")==1: #will apply inter-iteration filter
        inter_iter_filter_str=(
            "inter-iteration filter subiteration interval:= " + str(scannerParams.get("subiteration_interval")) +"\n" +
            "inter-iteration filter type := Separable Cartesian Metz \n" +
            "  Separable Cartesian Metz Filter Parameters := \n" +
            "  x-dir filter FWHM (in mm):= " + str(scannerParams.get("x_dir_filter_FWHM"))+ "\n" +
            "  y-dir filter FWHM (in mm):= " + str(scannerParams.get("y_dir_filter_FWHM"))+ "\n" +
            "  z-dir filter FWHM (in mm):= " + str(scannerParams.get("z_dir_filter_FWHM"))+ "\n" +
            "  x-dir filter Metz power:= 0.0 \n" +
            "  y-dir filter Metz power:= 0.0 \n" +
            "  z-dir filter Metz power:= 0.0 \n" +
            "END Separable Cartesian Metz Filter Parameters := \n\n" )
    else:
        inter_iter_filter_str= ""

    recFileName = join(output_dir,"rec_OSEM2D")    
    sensitFileName = join(output_dir,"sens.v")
    paramsFile = join(output_dir,"ParamsOSEM2D.par")
    new_file = open(paramsFile, "w")
      
    new_file.write(
            "OSMAPOSLParameters  :=\n\n" + 
            "objective function type := PoissonLogLikelihoodWithLinearModelForMeanAndProjData\n" +
            "PoissonLogLikelihoodWithLinearModelForMeanAndProjData Parameters := \n\n" +
            "input file := " + sinoFileName + "\n" +
            "maximum absolute segment number to process := 0 \n" +
            "zero end planes of segment 0 := 0 \n" +
            "sensitivity filename := " + sensitFileName + "\n" +
            "recompute sensitivity := 1 \n" +
            "use subset sensitivities := 0 \n\n" +
            "projector pair type := Matrix \n" +
            "Projector Pair Using Matrix Parameters := \n" +
            "Matrix type := Ray Tracing \n" +
            "Ray tracing matrix parameters := \n" +
            "number of rays in tangential direction to trace for each bin:= 5 \n" +
            "End Ray tracing matrix parameters := \n" +
            "End Projector Pair Using Matrix Parameters := \n\n" +
            att_corr_str +
            "prior type := FilterRootPrior \n" +
            "FilterRootPrior Parameters := \n" +
            "penalisation factor := 0. \n" +
            "Filter type := Median \n" +
            "Median Filter Parameters := \n" +
            "mask radius x := 1 \n" +
            "mask radius y := 1 \n" +
            "mask radius z := 1 \n" +
            "End Median Filter Parameters:= \n" +
            "END FilterRootPrior Parameters := \n\n" +
            scatt_corr_str +
            "zoom := " + str(zoom_aux) + "\n" +
            "xy output image size (in pixels) := " + str(xyOutputSize_aux) + "\n" 
            "Z output image size (in pixels) := " + str(zOutputSize) + "\n\n" +
            "end PoissonLogLikelihoodWithLinearModelForMeanAndProjData Parameters := \n\n" +
            "number of subsets := " + str(numberOfSubsets) + "\n" +
            "number of subiterations := " + str(numberOfIterations) + "\n" +
            "save estimates at subiteration intervals := " + str(savingInterval) + "\n\n" +
            "enforce initial positivity condition:=0 \n\n" +
            inter_iter_filter_str +
            "output filename prefix := " + recFileName + "\n\n" +
            "END := \n" 
            )

    new_file.close()

    command = '%s %s >> %s' % (recons, paramsFile, log_file)
    tools.osrun(command, log_file)        
            
    output = recFileName + "_" + str(scannerParams.get("numberOfIterations")) + ".hv"
    output = tools.anything_to_hdr_convert(output,log_file)
    if zoom!=zoom_aux:
        output = tools.resampleXYvoxelSizes(output, xyVoxelSize, log_file)

    return output

def OSEM3D_recons(config, scannerParams, sinograms_stir, additive_sino_stir, att_stir, output_dir, log_file):
        
    stir_dir = config.get("dir_stir")
    recons = join(stir_dir,'bin','OSMAPOSL')

    max_segment = scannerParams.get("max_segment")
    zoom = scannerParams.get("zoomFactor")
    xyOutputSize = scannerParams.get("xyOutputSize")
    zOutputSize =scannerParams.get("zOutputSize")
    numberOfSubsets = scannerParams.get("numberOfSubsets")
    numberOfIterations = scannerParams.get("numberOfIterations")
    savingInterval = scannerParams.get("savingInterval")
    
    if scannerParams.get("stir_recons_att_corr")==1:
        att_corr_str = (
        "Bin Normalisation type := From ProjData \n" +
        "Bin Normalisation From ProjData := \n" +
        "normalisation projdata filename:= "+ att_stir + "\n" +
        "End Bin Normalisation From ProjData:= \n")
    else:
        att_corr_str = ""
                        
    if scannerParams.get("stir_scatt_corr_smoothing") ==1: # Will use smoothed SimSET scatter as additive_sinogram.
        scatt_corr_str = ("additive sinogram := " + additive_sino_stir + "\n\n")
    else:
        scatt_corr_str = ""
        
    if scannerParams.get("inter_iteration_filter")==1: #will apply inter-iteration filter
        inter_iter_filter_str=(
            "inter-iteration filter subiteration interval:= " + str(scannerParams.get("subiteration_interval")) +"\n" +
            "inter-iteration filter type := Separable Cartesian Metz \n" +
            "  Separable Cartesian Metz Filter Parameters := \n" +
            "  x-dir filter FWHM (in mm):= " + str(scannerParams.get("x_dir_filter_FWHM"))+ "\n" +
            "  y-dir filter FWHM (in mm):= " + str(scannerParams.get("y_dir_filter_FWHM"))+ "\n" +
            "  z-dir filter FWHM (in mm):= " + str(scannerParams.get("z_dir_filter_FWHM"))+ "\n" +
            "  x-dir filter Metz power:= 0.0 \n" +
            "  y-dir filter Metz power:= 0.0 \n" +
            "  z-dir filter Metz power:= 0.0 \n" +
            "END Separable Cartesian Metz Filter Parameters := \n\n" )
    else:
        inter_iter_filter_str= ""

    recFileName = join(output_dir,"rec_OSEM3D")
    sensitFileName = join(output_dir,"sens.v")
    paramsFile = join(output_dir,"ParamsOSEM3D.par")
    new_file = open(paramsFile, "w")
      
    new_file.write(
            "OSMAPOSLParameters  :=\n\n" +
            "objective function type := PoissonLogLikelihoodWithLinearModelForMeanAndProjData\n" +
            "PoissonLogLikelihoodWithLinearModelForMeanAndProjData Parameters := \n\n" +
            "input file := " + sinograms_stir + "\n" +
            "maximum absolute segment number to process := " + str(max_segment)+ "\n" +
            "zero end planes of segment 0 := 0 \n" +
            "sensitivity filename := " + sensitFileName + "\n" +
            "recompute sensitivity := 1 \n" +
            "use subset sensitivities := 0 \n\n" +
            "projector pair type := Matrix \n" +
            "Projector Pair Using Matrix Parameters := \n" +
            "Matrix type := Ray Tracing \n" +
            "Ray tracing matrix parameters := \n" +
            "number of rays in tangential direction to trace for each bin:= 5 \n" +
            "End Ray tracing matrix parameters := \n" +
            "End Projector Pair Using Matrix Parameters := \n\n" +
            att_corr_str +
            "prior type := FilterRootPrior \n" +
            "FilterRootPrior Parameters := \n" +
            "penalisation factor := 0 \n" +
            "Filter type := Median \n" +
            "Median Filter Parameters := \n" +
            "mask radius x := 1 \n" +
            "mask radius y := 1 \n" +
            "mask radius z := 1 \n" +
            "End Median Filter Parameters:= \n" +
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
            inter_iter_filter_str +
            "output filename prefix := " + recFileName + "\n\n" +
            "END := \n"
            )

    new_file.close()

    command = '%s %s >> %s' % (recons, paramsFile, log_file)
    tools.osrun(command, log_file)
            
    output = recFileName + "_" + str(scannerParams.get("numberOfIterations")) + ".hv"
       
    output = tools.anything_to_hdr_convert(output,log_file)

    return output
