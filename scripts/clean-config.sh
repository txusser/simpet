#!/bin/bash

yq eval \
    '.interactive_mode = 0 | 
    .dir_stir = "" | 
    .dir_simset = "" | 
    .matlab_mcr_path = "" | 
    .spm_path = "" | 
    .dir_data_path = "" | 
    .dir_results_path = "" | 
    .interactive_mode = 0 | 
    .stratification = "true" | 
    .forced_detection = "true" | 
    .forced_non_absortion = "true" | 
    .acceptance_angle = 90.0 | 
    .positron_range =  "true" | 
    .isotope = "f18" | 
    .non_colinearity = "true" | 
    .minimum_energy = 350.0 | 
    .weight_window_ratio = 1.0 | 
    .point_source_voxels = "false" | 
    .coherent_scatter_object = "false" | 
    .coherent_scatter_detector = "false"' -

