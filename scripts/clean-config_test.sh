#!/bin/bash

export DIR_STIR='${root_path:root}/include/STIR/install'
export DIR_SIMSET='${root_path:root}/include/SimSET/2.9.2'

yq eval \
    '.defaults[0].params = "test" |
    .interactive_mode = 0 | 
    .dir_stir = "$DIR_STIR" | 
    .dir_simset = "$DIR_SIMSET" | 
    .matlab_mcr_path = "" | 
    .spm_path = "" | 
    .dir_data_path = null | 
    .dir_results_path = null | 
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

