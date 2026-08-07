import sys
import math  #new
from os.path import join, dirname
import nibabel as nib
import numpy as np
import os
from nibabel.processing import resample_from_to
from scipy.ndimage import zoom
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
from itertools import product
from pyprojroot import here

sys.path.append(str(here()))
from utils import resources as rsc
from utils import spm_tools as spm
from utils import tools
from src.stir import stir_tools

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

    def __init__(self, spm_run, maps_path, log, ct_path, pet_path):

        # Maps Paths
        self.analysis_path = dirname(pet_path)
        self.maps_path = maps_path
        self.ct_img = ct_path
        self.pet_img = pet_path
        # SPM
        self.spm_run = spm_run
        # Logging
        self.log_file = log
        self.act_smooth_value = 4
        self.nbins_act = 64
        self.log = log

    def run(self):

        pet_fus = self.pet_img[0:-3] + "img"
        ct_fus = self.ct_img[0:-3] + "img"

        mfile = join(self.maps_path, "fusion.m")
        coreg_simpet_img = spm.image_fusion(self.spm_run, mfile, ct_fus, pet_fus, self.log_file)
        self.pet_img = coreg_simpet_img[0:-3] + "hdr"

        self.ct_bilinear_hounsfield()
        self.pet_to_actmap()

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
        ct_data = tools.fix_4d_data(ct_image.get_fdata())

        ct_data = median_filter(ct_data, 4)
        att_data = ct_data

        indx = np.where((-200 < ct_data) & (ct_data <= 0))
        att_data[indx] = (u_PET_water * (ct_data[indx] + 1000)) / 1000
        indx = np.where(ct_data > 0)
        att_data[indx] = u_PET_water + ct_data[indx] * (u_CT_water / 1000) * (
                    (u_PET_bone - u_PET_water) / (u_CT_bone - u_CT_water))
        indx = np.where(ct_data <= -200)
        att_data[indx] = 0

        ctmax = np.amax(att_data)

        bins = np.linspace(0.09, 0.105, self.nbins_act)
        binned_ct_data = np.digitize(att_data, bins=bins)

        att_out = join(self.maps_path, 'att_binned.hdr')
        att_img = nib.AnalyzeImage(binned_ct_data, ct_image.affine, ct_image.header)
        nib.save(att_img, att_out)

        att_map = np.zeros_like(binned_ct_data)

        # Translation of CT mask to SimSET indices
        # Fat
        indx = np.where(binned_ct_data == 26)
        att_map[indx] = 23
        # Soft tissue
        indx = np.where((binned_ct_data > 26) & (binned_ct_data <= 32))
        att_map[indx] = 23
        # Hard tissue and muscle
        indx = np.where((binned_ct_data > 32) & (binned_ct_data <= 43))
        att_map[indx] = 7
        # Bone
        indx = np.where(binned_ct_data > 43)
        att_map[indx] = 3

        att_out = join(self.maps_path, 'att_segment.hdr')
        att_img = nib.AnalyzeImage(att_map, ct_image.affine, ct_image.header)
        nib.save(att_img, att_out)

        att_simset = join(self.maps_path, 'att_simset_it0.hdr')

        rcommand = '%s %s %s 1B >> %s' % (change_format, att_out, att_simset, self.log)
        tools.osrun(rcommand, self.log)

    def pet_to_actmap(self):
        """
        Transforms (sort of) a PET image into an activity map. 
        """
        # Starts login
        message = 'I am generating an activity map....'
        print(message)

        pet_image = nib.load(self.pet_img)
        pet_data = tools.fix_4d_data(pet_image.get_fdata())

        pet_data = median_filter(pet_data, 6)

        nan = np.where(np.isnan(pet_data))
        pet_data[nan] = 0

        mask_data = np.zeros_like(pet_data)
        pet_data_max = np.nanmax(pet_data)

        indx = np.where(pet_data > 0.001 * pet_data_max)
        mask_data[indx] = 1

        pet_out = join(self.maps_path, 'pet_denoised.hdr')
        act_img = nib.AnalyzeImage(pet_data, pet_image.affine, pet_image.header)
        nib.save(act_img, pet_out)

        mask_out = join(self.maps_path, 'pet_mask.hdr')
        mask_img = nib.AnalyzeImage(mask_data, pet_image.affine, pet_image.header)
        nib.save(mask_img, mask_out)

        att_out_binned = join(self.maps_path, 'att_binned.hdr')
        ct_image = nib.load(att_out_binned)
        ct_data = tools.fix_4d_data(ct_image.get_fdata())

        act_map_1 = np.zeros_like(ct_data)

        for i in range(1, self.nbins_act + 1):
            indx = np.where(ct_data == i)
            mean_pet = np.average(pet_data[indx])
            act_map_1[indx] = mean_pet

        att_segment = join(self.maps_path, 'att_segment.hdr')
        ct_image = nib.load(att_segment)
        ct_data = tools.fix_4d_data(ct_image.get_fdata())

        act_map_2 = np.zeros_like(ct_data)

        for i in range(23, 7, 3):
            indx = np.where(ct_data == i)
            mean_pet = np.average(pet_data[indx])
            act_map_2[indx] = mean_pet

        indx = np.where((act_map_1 != 0) & (pet_data != 0))

        act_map = np.zeros_like(ct_data)

        act_map[indx] = (act_map_1[indx] + act_map_2[indx] + pet_data[indx]) / 3
        # act_map[indx] = (act_map_1[indx]+act_map_2[indx])/3

        act_map = gaussian_filter(act_map, 1)

        act_max = np.amax(act_map)

        bins = np.linspace(0.01 * act_max, 0.40 * act_max, 126)
        binned_act = np.digitize(act_map, bins=bins) + mask_data

        act_out = join(self.maps_path, 'act.hdr')
        act_img = nib.AnalyzeImage(act_map, pet_image.affine, pet_image.header)
        nib.save(act_img, act_out)

        act_out = join(self.maps_path, 'act_simset_it0.hdr')
        act_img = nib.AnalyzeImage(binned_act, pet_image.affine, pet_image.header)
        nib.save(act_img, act_out)

        rcommand = '%s %s %s 1B >> %s' % (change_format, act_out, act_out, self.log)
        tools.osrun(rcommand, self.log)

def calculate_center_slices(self, act_map, scanner, zmin, zmax, overlapping=0.1):
    """Calculate the center slices of beds for the given axial range."""

    # Load activity map to get voxel size
    act_img = nib.load(act_map)
    self.z_voxsize = abs(act_img.affine[2, 2])  # Axial voxel size (mm)

    # Compute axial range
    z_nvoxels = zmax - zmin
    act_z_length = z_nvoxels * self.z_voxsize  # mm

    axial_fov = scanner.get("axial_fov") * 10  # mm
    whole_body_simulation = self.params.get("whole_body_simulation")
    
    beds_cs = []

    # Single bed case
    if whole_body_simulation == 0 or act_z_length <= axial_fov:
        beds_cs = [self.params.get("center_slice")]

        print(
            "A single bed position is used because:\n"
            "- The map length is smaller than the axial FOV, or\n"
            "- Whole-body simulation is disabled."
        )

    else:
        # Effective FOV considering overlap
        eff_aFOV = axial_fov * (1 - 2 * overlapping)

        if eff_aFOV <= 0:
            raise ValueError("Overlapping too large. Effective axial FOV <= 0.")

        # Determine number of beds
        self.Bed_to_do = max(1, math.ceil(act_z_length / eff_aFOV))

        # Number of voxels per bed
        self.voxels_per_bed = max(1, int(np.ceil(z_nvoxels / self.Bed_to_do)))

        # First bed center
        bed_center = zmin + self.voxels_per_bed / 2
        beds_cs.append(int(np.rint(bed_center)))

        # Additional beds
        while len(beds_cs) < self.Bed_to_do:
            bed_center += self.voxels_per_bed

            if bed_center + self.voxels_per_bed / 2 > zmax:
                break

            beds_cs.append(int(np.rint(bed_center)))

    self.beds_cs = beds_cs
    return beds_cs

def update_act_map(spmrun, act_map, att_map, orig_pet, simu_pet, output):
    output_dir = dirname(output)
    mfile = join(dirname(output), "fusion.m")
    log_file = join(dirname(output), "fusion.log")

    # First step is coregistering the output image with the act map
    act_map_img = act_map[0:-3] + "img"
    simu_pet_img = simu_pet[0:-3] + "img"
    orig_pet_img = orig_pet[0:-3] + "img"
    coreg_simpet_img = spm.image_fusion(spmrun, mfile, act_map_img, simu_pet_img, log_file)
    coreg_simpet_hdr = coreg_simpet_img[0:-3] + "hdr"

    # Once done we load the images
    simpet = nib.load(coreg_simpet_hdr)
    simpet_data = tools.fix_4d_data(simpet.get_fdata())
    tools.remove_neg_nan(simpet_data)

    origpet = nib.load(orig_pet)
    origpet_data = tools.fix_4d_data(origpet.get_fdata())
    tools.remove_neg_nan(origpet_data)

    act = nib.load(act_map)
    act_data = tools.fix_4d_data(act.get_fdata())
    tools.remove_neg_nan(act_data)

    att = nib.load(att_map)
    att_data = tools.fix_4d_data(att.get_fdata())
    tools.remove_neg_nan(att_data)

    # Next we will do a scaling by the mean (We use the dense tissue as a reference region)
    indx = np.where(att_data == 7)

    mean_simpet = np.nanmean(simpet_data[indx])
    mean_orig = np.nanmean(origpet_data[indx])
    print(mean_simpet)
    print(mean_orig)
    scaling_factor = mean_orig / mean_simpet
    simpet_data = simpet_data * scaling_factor

    # Now we do a smoothing of both data to avoid multiply noise and perform the division
    simpet_data = median_filter(simpet_data, 5)
    origpet_data = median_filter(origpet_data, 5)

    div_out = join(output_dir, "smooth_sim.hdr")
    smoothpet_img = nib.AnalyzeImage(simpet_data, simpet.affine, simpet.header)
    nib.save(smoothpet_img, div_out)

    div_out = join(output_dir, "smooth_orig.hdr")
    smoothpet_img = nib.AnalyzeImage(origpet_data, simpet.affine, simpet.header)
    nib.save(smoothpet_img, div_out)

    division = origpet_data / simpet_data

    division[np.isnan(division)] = 0

    indx = np.where(division > 3)
    division[indx] = 3
    indx = np.where(division <= 0)
    division[indx] = 0

    division = median_filter(division, 10)

    mask_data = np.zeros_like(origpet_data)
    indx = np.where(origpet_data > 0.001 * np.nanmax(origpet_data))
    mask_data[indx] = 1
    division = division * mask_data

    mask_data_2 = np.zeros_like(simpet_data)
    indx = np.where(simpet_data < 0.001 * np.nanmax(simpet_data))
    division[indx] = 1

    div_out = join(output_dir, "division.hdr")
    div_img = nib.AnalyzeImage(division, simpet.affine, simpet.header)
    nib.save(div_img, div_out)

    # We update the act
    updated_act = division * act_data
    # updated_act[indx] = act_data[indx]

    print(np.nanmax(updated_act))

    bins = np.linspace(0, np.nanmax(updated_act), 127)
    updated_act = np.digitize(updated_act, bins=bins)
    updated_act = updated_act * mask_data

    updated_act_img = nib.AnalyzeImage(updated_act, simpet.affine, simpet.header)
    nib.save(updated_act_img, output)

def cut_image_min_max_slices(input_img, min_slice, max_slice, output):
    img = nib.load(input_img)
    img_data = tools.fix_4d_data(img.get_fdata())

    img_data = img_data[:, :, min_slice:max_slice]

    hdr1 = nib.AnalyzeHeader()
    dtype = img.get_data_dtype()
    hdr1.set_data_dtype(dtype)
    hdr1.set_data_shape(img_data.shape)
    affine = img.get_affine()
    hdr1.set_zooms((abs(affine[0, 0]), abs(affine[1, 1]), abs(affine[2, 2])))

    analyze_img = nib.AnalyzeImage(img_data, hdr1.get_base_affine(), hdr1)
    nib.save(analyze_img, output)

    return output

def calculate_map_into_fov(self, act_map):
    """
    Limits of the FOV per bed (map_into_FOV_start/end). 
    It is necessary to apply correction_for_NECR and join_beds_wb
    """
    act = nib.load(act_map)
    beds_cs = calculate_center_slices(self, act_map, self.scanner, self.zmin, self.zmax)

    zmin = int(self.zmin)
    zmax = int(self.zmax)

    axial_fov = int(self.scanner["axial_fov"] * 10)  # mm
    map_voxel_size = float(round(act.affine[2, 2], 3)) # axial voxels size
    half_fov_slices = (axial_fov / 2) / map_voxel_size

    self.map_into_FOV_start = []
    self.map_into_FOV_end = []

    for j, cs in enumerate(beds_cs, start=1):
        
        # Slices into the FOV
        map_into_FOV_start = int(round(cs - half_fov_slices))
        map_into_FOV_end = int(round(cs + half_fov_slices))
        
        #Remove
        #print(f"Before correction: start={map_into_FOV_start}, end={map_into_FOV_end}")

        if map_into_FOV_start < zmin:
            map_into_FOV_start = zmin
        else:
            map_into_FOV_start = int(round(cs - half_fov_slices))
        
        if map_into_FOV_end > zmax:
            map_into_FOV_end = zmax
        else:
            map_into_FOV_end = int(round(cs + half_fov_slices))
        
        # Save start and end slice for each bed position
        self.map_into_FOV_start.append(map_into_FOV_start)
        self.map_into_FOV_end.append(map_into_FOV_end)

        print(f"\nNumbers of Slices inside of FOV: [{map_into_FOV_start} , {map_into_FOV_end}]")

def correction_for_NECR(self, act_map, sim_time_original):

    #Activity correction according to the bed (Bruker PET/MRI)
    act = nib.load(act_map)
    act_data = act.get_fdata()
    
    self.params = self.cfg["params"]
    self.sim_dose = float(self.params.get("total_dose", 0))
    self.add_randoms = int(self.params.get("add_randoms", 0))
    
    #Map into FOV
    calculate_map_into_fov(self, act_map)
    
    self.phantom_doses_FOV = []
    sim_times_per_bed = []

    zmin = int(self.zmin)
    zmax = int(self.zmax)

    for j, (map_start, map_end) in enumerate(zip(self.map_into_FOV_start, self.map_into_FOV_end), start=1):

        #Activity at the time of acquisition according to the bed
        phantom_counts_FOV = np.sum(act_data[:, :, int(map_start): int(map_end)])
        phantom_counts_total = np.sum(act_data[:, :, :])
        self.ratio_act_fov = abs (phantom_counts_FOV / phantom_counts_total)
        
        self.phantom_dose_FOV = float(round(abs(self.sim_dose * self.ratio_act_fov), 3))
        self.phantom_doses_FOV.append(self.phantom_dose_FOV)

        #TODO Use the fitted equation.
        if self.add_randoms ==1:
            y = abs(4.55 * self.phantom_dose_FOV + 1.9775)
        else:
            y = abs (4.569 * self.phantom_dose_FOV + 1.959)

        
        print(f"\nBeds_to_perform: {j}")
        print(f"Simulation Dose inside FOV: {float(round(self.phantom_dose_FOV, 3))} mCi")
            
        sim_time_bed = float(sim_time_original / y)
        sim_time_bed = float(round(sim_time_bed, 1))
        sim_times_per_bed.append(sim_time_bed) 

        print(f"Corrected simulation time = {sim_time_bed} seg") 
      

        # ####Remove
        # #labels into each beds
        # # Extract only the portion of the map within the FOV (Z-axis)
        # # Assuming that axis 2 (index 2) is the Z-axis
        act_data_FOV = act_data[:, :, map_start:map_end]
        # # Get the labels within that range (excluding the background label, 0)
        labels = np.unique(act_data_FOV)
        labels = labels[labels != 0]

        # Contar voxeles por label dentro del FOV
        voxel_counts = [np.sum(act_data_FOV == label) for label in labels]
        phantom_voxel_volumen = abs(np.prod(act.header.get_zooms()[:3]) / 1000) #cm^3
        volumes_region = [count * phantom_voxel_volumen for count in voxel_counts]

        phantom_act = nib.load(act_map)
        phantom_act_data = phantom_act.get_fdata()
        phantom_voxel_volumen = abs(np.prod(phantom_act.header.get_zooms()[:3]) / 1000) #cm^3
        total_phantom_counts = np.sum(phantom_act_data)
    
        #Calculate the factor to convert to real phantom activity
        if self.sim_dose != 0:
            phantom_dose = abs(total_phantom_counts * phantom_voxel_volumen)  # uCi
            print(f"phantom_dose: {phantom_dose} au")
            self.act_table_factor = self.sim_dose * 1000 / phantom_dose
        else:
            self.act_table_factor = 1
    

        new_concent_label = [a * self.act_table_factor for a in labels]
        activity_region_uCi = [m * v for m, v in zip(new_concent_label, volumes_region)]
        actividad_total_mCi = sum(activity_region_uCi)/1000

        print(f"Actividad Total: {actividad_total_mCi} mCi")

        # Mostrar resumen por cama
        print(f"\nBed {j}:")
        for lbl, vox , volum, concent, act_mCi in zip(labels, voxel_counts, volumes_region, new_concent_label, activity_region_uCi):
            print(f"  Label {lbl}: {vox} voxeles dentro del FOV, Volumen de region {volum}, New_concentration: {concent}uci/cc, Activity uCi: {act_mCi}")
    
    return sim_times_per_bed, self.phantom_doses_FOV

def join_beds_wb(self, act_map, recons_beds, joint_beds):
    """
    Joins the reconstructed beds correcting overlap dynamically.
    The trimming is split half to the previous bed and half to the next.
    Saves the final image in Analyze format (.hdr/.img) as in the original function.
    """
    #Map into FOV
    calculate_map_into_fov(self, act_map)
    
    # Load activity map to get voxel size
    act = nib.load(act_map)
    act_voxel_size = float(round(act.affine[2, 2], 3))  # mm

    # Load first bed
    bed_prev = nib.load(recons_beds[0])
    bed_prev_data = tools.fix_4d_data(bed_prev.get_fdata())
    img_recons_voxel_size = float(round(bed_prev.affine[2, 2], 3))    #mm

    for i in range(len(recons_beds) - 1):
        # Load next bed
        bed_next = nib.load(recons_beds[i + 1])
        bed_next_data = tools.fix_4d_data(bed_next.get_fdata())

        # Calculate total dynamic trimming (only if there is overlap)
        end_i = self.map_into_FOV_end[i]
        start_next = self.map_into_FOV_start[i + 1]
        diff = end_i - start_next

        if diff > 0:
            slices_to_remove = int(round((diff * act_voxel_size) / img_recons_voxel_size))
        else:
            slices_to_remove = 0  # No overlap

        # Split the trimming evenly
        remove_prev = slices_to_remove // 2
        remove_next = slices_to_remove - remove_prev  # covers the rest if odd

        print(f"Bed {i} end={end_i}, Bed {i+1} start={start_next} → diff={diff}, total remove={slices_to_remove}, remove_prev={remove_prev}, remove_next={remove_next}")

        # Trim previous bed (last slices)
        if remove_prev > 0 and remove_prev < bed_prev_data.shape[2]:
            bed_prev_data = bed_prev_data[:, :, :-remove_prev]

        # Trim next bed (first slices)
        if remove_next > 0 and remove_next < bed_next_data.shape[2]:
            bed_next_data = bed_next_data[:, :, remove_next:]

        # Concatenate beds
        bed_prev_data = np.append(bed_prev_data, bed_next_data, axis=2)
    
    # --- Apply final flips as in the original function ---
    bed_prev_data = np.flipud(bed_prev_data)
    #bed_prev_data = np.fliplr(bed_prev_data)

    # --- Save the concatenated image as in the original function ---
    hdr1 = nib.AnalyzeHeader()
    dtype = bed_prev.get_data_dtype()
    hdr1.set_data_dtype(dtype)
    hdr1.set_data_shape(bed_prev_data.shape)
    affine = bed_prev.get_affine()
    hdr1.set_zooms((abs(affine[0, 0]), abs(affine[1, 1]), abs(affine[2, 2])))

    analyze_img = nib.AnalyzeImage(bed_prev_data, hdr1.get_base_affine(), hdr1)
    nib.save(analyze_img, joint_beds)

    print(f"\nConcatenated image saved at: {joint_beds}")
    print(f"Data Type: {dtype}")
    print(f"Matrix Size: {bed_prev_data.shape}")
    print(f"Voxel Size: {hdr1.get_zooms()}")

def normalization_factor_correction(self):
    #factor_Q_norm = 400.13   #480.43
    results = []

    print(f"Phantom dose (FOV):{self.phantom_doses_FOV}")

    for dose_mCi in self.phantom_doses_FOV:
        # Convert mCi to kBq
        phantom_dose_KBq = dose_mCi * 3.7e4  
        sim_time_original_global = float(self.params.get("simulation_time", 0))
        print(f"Phantom dose in KBq: {phantom_dose_KBq}") 

        # Linear adjustment equation
        #lineal_ecuac = 5.9e-5 * phantom_dose_KBq + 0.978
        #value_Q_norm = float(lineal_ecuac * factor_Q_norm)
        #value_Q_norm = float(0.061 * phantom_dose_KBq + 904.2)
        concentrac = (phantom_dose_KBq / 98.96)
        print(f"Phantom conc in KBq/cc: {concentrac}")
        

        #voi 30 x 140 Imagen Simulada vs Concentracion teorica experimental
        value_Q_norm = float(0.062 * (phantom_dose_KBq) + 986.39)

        value_Q_norm_corregido_time = value_Q_norm / (sim_time_original_global/300)  # 300 seg es el tiempo de adq cyl calibración
        #print(f"Normalization value per bed: {value_Q_norm}")
        #results.append(value_Q_norm)
        results.append(value_Q_norm_corregido_time)


        if len(results) == 0:
            print(f"There is no FOV dose. Using factor = 1.0 by default")
            return 1.0

    print("Normalization factors by FOV:", [round(x, 3) for x in results])
    return results 

def rotate_and_flip_mask(act_map, mask_map, rotated_mask_file, joint_beds, zmin, zmax):
    """
    Rotates and flips a NIfTI mask (mask_map) based on the best alignment
    calculated from act_map compared to a reference (joint_beds).

    PARAMETERS:
    - act_map: path to activity map NIfTI
    - mask_map: path to mask NIfTI to be rotated/flipped
    - rotated_mask_file: output path for transformed mask
    - joint_beds: path to reference NIfTI
    - zmin, zmax: axial range of interest (inclusive, MRIcro-style)

    IMPORTANT:
    - Original voxel intensities in mask_map are preserved.
    - Binarization is performed ONLY on a copy of act_map for Dice calculation.
    - Final transformation is applied to mask_map.
    """

    def overlap_coefficient(a, b):
        """Computes overlap similarity between two binary masks."""
        a = a > 0
        b = b > 0
        intersection = np.sum(a & b)
        return 2 * intersection / (np.sum(a) + np.sum(b) + 1e-8)

    def crop_z(data, zmin, zmax):
        """
        Crops a volume along the axial axis including zmin and zmax (MRIcro-style, inclusive)
        """
        zmin = int(zmin)
        zmax = int(zmax)

        zmax = zmax -1
        if zmax is None:
            zmax = data.shape[2]
        zmin_adj = max(0, zmin - 1)            # Ajuste inicio 0-indexed Python
        zmax_adj = min(zmax, data.shape[2] - 1)  # Ajuste fin
        return data[:, :, zmin_adj:zmax_adj + 1]  # +1 para incluir zmax

    try:
        # --- Load mask to transform ---
        mask_img = nib.load(mask_map)
        mask_data_original = mask_img.get_fdata()
        if mask_data_original.ndim == 4 and mask_data_original.shape[3] == 1:
            mask_data_original = np.squeeze(mask_data_original, axis=3)
        mask_data_original = crop_z(mask_data_original, zmin, zmax)

        # --- Load act_map for calculating best transform ---
        act_img = nib.load(act_map)
        act_data = act_img.get_fdata()
        if act_data.ndim == 4 and act_data.shape[3] == 1:
            act_data = np.squeeze(act_data, axis=3)
        act_data = crop_z(act_data, zmin, zmax)
        act_data_binary = (act_data > 0).astype(np.uint8)

        # --- Load reference ---
        ref_img = nib.load(joint_beds)
        ref_data = ref_img.get_fdata()
        if ref_data.ndim == 4 and ref_data.shape[3] == 1:
            ref_data = np.squeeze(ref_data, axis=3)
        ref_data = crop_z(ref_data, zmin, zmax)
        ref_data_binary = (ref_data > 0).astype(np.uint8)

        # --- Rescale act_map binary for overlap computation ---
        act_voxel_size = act_img.header.get_zooms()[:3]
        ref_voxel_size = ref_img.header.get_zooms()[:3]
        scale_factors = np.array(act_voxel_size) / np.array(ref_voxel_size)
        act_rescaled = zoom(act_data_binary, zoom=scale_factors, order=0, prefilter=False)

        # --- Pad volumes for overlap computation ---
        max_shape = np.maximum(act_rescaled.shape, ref_data_binary.shape)

        def pad_to_shape(data, target_shape):
            pad_width = []
            for s, t in zip(data.shape, target_shape):
                total = t - s
                before = total // 2
                after = total - before
                pad_width.append((before, after))
            return np.pad(data, pad_width, mode='constant', constant_values=0)

        act_padded = pad_to_shape(act_rescaled, max_shape)
        ref_padded = pad_to_shape(ref_data_binary, max_shape)

        # --- Search best rotation/flip using act_map ---
        best_score = -1
        best_transform = (0, False, False)

        for k in range(4):
            rotated = np.rot90(act_padded, k=k, axes=(0, 1))
            for flip_x, flip_y in product([False, True], repeat=2):
                candidate = rotated.copy()
                if flip_x:
                    candidate = np.flip(candidate, axis=0)
                if flip_y:
                    candidate = np.flip(candidate, axis=1)

                score = overlap_coefficient(candidate, ref_padded)
                if score > best_score:
                    best_score = score
                    best_transform = (k, flip_x, flip_y)

        # --- Apply best transform to ORIGINAL mask_map data ---
        transformed_mask = np.rot90(mask_data_original, k=best_transform[0], axes=(0, 1))
        if best_transform[1]:
            transformed_mask = np.flip(transformed_mask, axis=0)
        if best_transform[2]:
            transformed_mask = np.flip(transformed_mask, axis=1)

        # --- Save result ---
        new_affine = mask_img.affine.copy()
        final_img = nib.Nifti1Image(transformed_mask, affine=new_affine, header=mask_img.header.copy())
        final_img.set_qform(new_affine, code=1)
        final_img.set_sform(new_affine, code=1)

        if not rotated_mask_file.endswith(".nii"):
            rotated_mask_file = os.path.splitext(rotated_mask_file)[0] + ".nii"

        nib.save(final_img, rotated_mask_file)
        return rotated_mask_file

    except Exception as e:
        print("\n=== ERROR during rotate_and_flip_mask ===")
        print("Error type:", type(e))
        print("Message:", e)
        raise

def change_act_dimensions(mask, rotated_mask, joint_beds): 
    """
    Adjust a mask image to match reference voxel size and shape, padding with zeros if necessary.
    """
    # --- Load original image ---
    img = nib.load(rotated_mask)
    data = img.dataobj[:]  # preserve integers and avoid decimals

    if data.ndim == 4 and data.shape[3] == 1:
        data = np.squeeze(data, axis=3)

    shape = np.array(data.shape[:3])
    voxel_size = np.array(img.header.get_zooms()[:3])
    size_mm = shape * voxel_size
       
    # --- Load reference image ---
    recons_img = nib.load(joint_beds)
    recons_shape = np.array(recons_img.shape[:3])
    recons_voxel_sizes = np.array(recons_img.header.get_zooms()[:3])

    # --- Adjust resolution ---
    new_voxel_size = recons_voxel_sizes
    new_shape = np.round(size_mm / new_voxel_size).astype(int)
    scale_factor = new_shape / shape
    #print("Original Dimensions:", data.shape)
    #print("Scale Factor:", scale_factor)

    # --- Rescale volume (without continuous interpolation) ---
    new_data = zoom(data, zoom=scale_factor, order=0, prefilter=False)

    # --- Correct geometric origin to align center ---
    orig_center = (shape * voxel_size) / 2
    new_center = (new_shape * new_voxel_size) / 2
    shift = orig_center - new_center  # shift in mm

    # --- New header and affine ---
    new_affine = recons_img.affine.copy()
    new_affine = np.eye(4)                   # complete 4x4 matrix
    new_affine[:3, :3] = np.diag(new_voxel_size)
    new_affine[:3, 3] = np.zeros(3)    
    
    # --- Create header and affine ---
    nuevo_header = nib.Nifti1Header()
    nuevo_header.set_data_shape(new_data.shape)
    nuevo_header.set_zooms(new_voxel_size)

    # --- Create intermediate image ---
    final_image = nib.Nifti1Image(new_data, affine=new_affine, header=nuevo_header)

    # --- Symmetric padding to match reference shape ---
    final_shape = np.array(final_image.shape)
    diff = recons_shape - final_shape[:3]
    pad_width = []
    cropped_data = final_image.get_fdata()

    for i in range(3):
        if diff[i] >= 0:
            # Image is smaller - add zeros
            pad_width.append((diff[i] // 2, diff[i] - diff[i] // 2))
        else:
            # Image is larger - crop
            start = abs(diff[i]) // 2
            end = start + recons_shape[i]
            cropped_data = np.take(cropped_data, indices=range(start, end), axis=i)
            pad_width.append((0, 0))

    padded_data = np.pad(cropped_data, pad_width, mode='constant', constant_values=0)

    # --- Final adjustment to exact size ---
    final_data = padded_data
    for axis in range(3):
        if final_data.shape[axis] > recons_shape[axis]:
            start = (final_data.shape[axis] - recons_shape[axis]) // 2
            end = start + recons_shape[axis]
            final_data = np.take(final_data, indices=range(start, end), axis=axis)
        elif final_data.shape[axis] < recons_shape[axis]:
            pad_before = (recons_shape[axis] - final_data.shape[axis]) // 2
            pad_after = recons_shape[axis] - final_data.shape[axis] - pad_before
            final_data = np.pad(
                final_data,
                [(pad_before, pad_after) if ax == axis else (0, 0) for ax in range(3)],
                mode='constant',
                constant_values=0
            )

    # --- Create final NIfTI image ---
    final_padded_image = nib.Nifti1Image(final_data, affine=new_affine, header=nuevo_header)
    final_padded_image.set_qform(new_affine, code=1)
    final_padded_image.set_sform(new_affine, code=1)

    # --- Save final image ---
    nib.save(final_padded_image, mask)

    # --- Delete the .nii file ---
    base_name = os.path.splitext(rotated_mask)[0]  # remove the extension
    for f in [base_name + ".nii"]:
        if os.path.exists(f):
            os.remove(f)

    return final_padded_image

def total_quantification(mask_file, joint_norm_beds, quantification_file, label_file_mask):
    """
    Compute information of target image per labeled region in reference image and save to a TXT file.
    """

    import nibabel as nib
    import numpy as np
    import os

    # --- Load images ---
    target_img = nib.load(joint_norm_beds)
    roi_img = nib.load(mask_file)

    target_data = target_img.get_fdata()
    roi_data = roi_img.get_fdata().astype(int)

    # --- Ensure same shape ---
    if target_data.shape != roi_data.shape:
        raise ValueError("Target and reference images must have the same shape.")

    # --- Load label names ---
    label_names = {}

    if os.path.exists(label_file_mask):
        with open(label_file_mask, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()  # debe estar dentro del for
                label_id = int(parts[0])
                label_name = " ".join(parts[1:])
                label_names[label_id] = label_name
    else:
        print(f"INFO: Label file not found: {label_file_mask}. Using numeric labels from ROI.")



    # --- Get all labels in the mask except 0 (background) ---
    labels = np.unique(roi_data)
    labels = labels[labels != 0]

    # --- Calculate mean per label ---
    mean_values = [target_data[roi_data == label].mean() for label in labels]  # KBq/cc

    # --- Calculate volume per label ---
    voxel_counts = [np.sum(roi_data == label) for label in labels]
    dx, dy, dz = np.array(roi_img.header.get_zooms()[:3])
    voxel_volume = dx * dy * dz  # mm³
    volumes = [(count * voxel_volume) / 1000 for count in voxel_counts]  # cm³

    # --- Calculate activity per region ---
    activity_region_KBq = [m * v for m, v in zip(mean_values, volumes)]
    activity_region_mCi = [a / (3.7 * 10**4) for a in activity_region_KBq]
    mean_values_mCi = [b / c for b, c in zip(activity_region_mCi, volumes)]

    # --- Calculate TOTAL activity ---
    total_activity_KBq = float(np.sum(activity_region_KBq))
    total_activity_mCi = float(np.sum(activity_region_mCi))

    # --- Save report as TXT ---
    with open(quantification_file, 'w') as f:
        # Header
        f.write(
            f"{'Region':<15}{'MeanValue (mCi/cc)':>20}{'MeanValue (KBq/cc)':>20}"
            f"{'Pixels':>15}{'Vol (cm³)':>15}{'Act (mCi)':>15}{'Act (KBq)':>15}\n"
        )

        # Rows
        for label, mean_val_mCi, mean_val_KBq, count, vol, act_mCi, act_KBq in zip(
            labels, mean_values_mCi, mean_values,
            voxel_counts, volumes, activity_region_mCi, activity_region_KBq
        ):
            label_name = label_names.get(int(label), f"Label_{int(label)}")
            f.write(
                f"{label_name:<15}{mean_val_mCi:>20.4f}{mean_val_KBq:>20.4f}"
                f"{count:>15.0f}{vol:>15.4f}{act_mCi:>15.4f}{act_KBq:>15.4f}\n"
            )

        # Separator
        f.write("=" * 115 + "\n")

        # TOTAL
        f.write(
            f"{'TOTAL':<15}{'':>20}{'':>20}{'':>15}{'':>15}"
            f"{total_activity_mCi:>15.4f}{total_activity_KBq:>15.4f}\n"
        )

    return {
        "labels": labels,
        "label_names": label_names,
        "mean_values_mCi": mean_values_mCi,
        "mean_values_KBq": mean_values,
        "pixel_counts": voxel_counts,
        "volumes": volumes,
        "activity_mCi": activity_region_mCi,
        "activity_KBq": activity_region_KBq,
        "total_activity_mCi": total_activity_mCi,
        "total_activity_KBq": total_activity_KBq
    }
    
def distribution_of_dose_into_phantom(self, maps_dir, act_map, info_act_map, label_file_act_map):
    """
    Computes the actual distribution of activity by region labeled in act_map. 
    Obtains information about the actual distribution of activity in the phantom and saves it in a TXT file.
    """

    #Upload the act  image
    phantom_act = nib.load(act_map)
    phantom_act_data = phantom_act.get_fdata()
    phantom_voxel_volumen = abs(np.prod(phantom_act.header.get_zooms()[:3]) / 1000) #cm^3
    total_phantom_counts = np.sum(phantom_act_data)
    
    #Calculate the factor to convert to real phantom activity
    if self.sim_dose != 0:
        phantom_dose = abs(total_phantom_counts * phantom_voxel_volumen)  # uCi
        #print(f"phantom_dose: {phantom_dose} au")

        act_table_factor = self.sim_dose * 1000 / phantom_dose
    else:
        act_table_factor = 1
    
    #print(f"Factor_actividad: {act_table_factor}")
    #print(f"self.sim_dose: {self.sim_dose} mCi")
    #print(f"total_phantom_counts: {total_phantom_counts}")

    phantom_real_act = phantom_act_data * (act_table_factor/1000) #se multilica por mil para llevar los valores a mCi

    # Save the file into the same Folder of act_map with different name
    base_dir = os.path.dirname(act_map)
    name, ext = os.path.splitext(os.path.basename(act_map))

    if ext.lower() in [".hdr", ".img"]:
        output_path = os.path.join(base_dir, f"{name}_real.hdr")
    else:
        output_path = os.path.join(base_dir, f"{name}_real.nii")
    
    #New image with the real activity to simulate
    new_img = nib.Nifti1Image(phantom_real_act, affine=phantom_act.affine, header=phantom_act.header)
    # Save new image
    nib.save(new_img, output_path)

    # --- Load label names ---
    label_names = {}

    if label_file_act_map and os.path.exists(label_file_act_map):
        with open(label_file_act_map, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    # Linea invalida, ignorar
                    continue
                try:
                    label_id = int(parts[0])
                    label_name = " ".join(parts[1:])
                    label_names[label_id] = label_name
                except ValueError:
                    continue  # Si no se puede convertir a entero, ignorar
    else:
        print(f"No label file found: Using ROI numbers as labels")



    # --- Get labels ---
    labels = np.unique(phantom_act_data)
    labels = labels[labels != 0]

    # --- Calculate stats per label ---
    mean_values_mCi = [phantom_real_act[phantom_act_data == label].mean() for label in labels]
    voxel_counts = [np.sum(phantom_act_data == label) for label in labels]
    volumes_region = [count * phantom_voxel_volumen for count in voxel_counts]
    activity_region_mCi = [m * v for m, v in zip(mean_values_mCi, volumes_region)]
    activity_region_KBq = [a * 3.7 * 10**4 for a in activity_region_mCi]
    mean_values_KBq = [b / c for b, c in zip(activity_region_KBq, volumes_region)]

    total_activity_KBq = float(np.sum(activity_region_KBq))
    total_activity_mCi = float(np.sum(activity_region_mCi))

    # --- Save report as TXT ---
    with open(info_act_map, 'w') as f:
        f.write(f"{'Region':<15}{'MeanValue (mCi/cc)':>20}{'MeanValue (KBq/cc)':>20}"
                f"{'Pixels':>15}{'Vol (cm³)':>15}{'Act (mCi)':>15}{'Act (KBq)':>15}\n")

        for label, mean_val_mCi, mean_val_KBq, count, vol, act_mCi, act_KBq in zip(
                labels, mean_values_mCi, mean_values_KBq, voxel_counts, volumes_region, activity_region_mCi, activity_region_KBq):
            
            # Sustituir número por nombre
            label_name = label_names.get(int(label), str(int(label)))
            f.write(f"{label_name:<15}{mean_val_mCi:>20.4f}{mean_val_KBq:>20.4f}"
                    f"{count:>15.0f}{vol:>15.4f}{act_mCi:>15.4f}{act_KBq:>15.4f}\n")

        # Separador y total
        f.write("="*115 + "\n")
        f.write(f"{'TOTAL':<15}{'':>20}{'':>20}{'':>15}{'':>15}"
                f"{total_activity_mCi:>15.4f}{total_activity_KBq:>15.4f}\n")

    return {
        "image_path": output_path,
        "factor": act_table_factor,
        "labels": labels,
        "label_names": label_names,
        "mean_values_mCi": mean_values_mCi,
        "mean_values_KBq": mean_values_KBq,
        "volumes": volumes_region,
        "activity_mCi": activity_region_mCi,
        "activity_KBq": activity_region_KBq,
        "total_activity_mCi": total_activity_mCi,
        "total_activity_KBq": total_activity_KBq
    }

def coincidences_mask_vs_image(mask_file, act_map):  #Remove it is only a check
    # --- Verification of the label volumen  ---
    import numpy as np
    import nibabel as nib

    try:
        orig_img = nib.load(act_map)  # original image
        new_img  = nib.load(mask_file)
        
        orig_data = orig_img.get_fdata()
        new_data  = new_img.get_fdata()
        
        voxel_orig = np.prod(orig_img.header.get_zooms()[:3]) / 1000  # mm³ -> cm³
        voxel_new  = np.prod(new_img.header.get_zooms()[:3]) / 1000
        
        labels = np.unique(orig_data)
        labels = labels[labels != 0]
        
        
        print("\n--- Comparation of volumen per label ---")
        for label in labels:
            count_orig = np.sum(orig_data == label)
            count_new  = np.sum(new_data == label)
            vol_orig = count_orig * voxel_orig
            vol_new  = count_new * voxel_new
            ratio = vol_new / vol_orig if vol_orig > 0 else np.nan
            
            print(f"Label {int(label):3d}:  original={vol_orig:.3f} cm³,  new={vol_new:.3f} cm³,  ratio={ratio:.3f}")
    except Exception as e:
        print(f"Notice: Could not compare volumes by label: {e}")

def total_fov_correction(self, recons_dir):

    """
    This function performs the STIR reconstruction sinogram correction, if desired, 
    using a sinogram obtained from a cylinder that fills the entire FOV.
    IT IS RECOMMENDED TO NORMALIZE THE SINOGRAM USING ITS MEAN VALUE.
    """
    import shutil

    whole_FOV_dir_path = self.config.get("dir_stir_sino_corrections")
    whole_FOV_sino_file = os.path.join(whole_FOV_dir_path, "sinogram_TOTAL_FOV_divid_VM.img")
    whole_FOV_stir_sino = nib.load(whole_FOV_sino_file)
    #whole_FOV_stir_sino_data = whole_FOV_stir_sino.get_fdata()
    whole_FOV_stir_sino_data = np.squeeze(whole_FOV_stir_sino.get_fdata())
    
    if not whole_FOV_dir_path or not os.path.exists(whole_FOV_dir_path) or os.path.getsize(whole_FOV_dir_path) == 0:
        raise FileNotFoundError(f"The directory or file '{whole_FOV_dir_path}' does not exist or is empty.")


    stir_sino_path = os.path.join(recons_dir, "stir_sinogram")
    stir_sino_img = nib.load(stir_sino_path + ".img")
    stir_sinogram = stir_sino_img.get_fdata()

    # Division pixel per pixel, wherever where the pixel value is 0, the result will be 0
    corrected_sinogram = np.where(whole_FOV_stir_sino_data == 0, 0, stir_sinogram / whole_FOV_stir_sino_data)
    corrected_img = nib.AnalyzeImage(corrected_sinogram, affine=stir_sino_img.affine, header=stir_sino_img.header)

    #Output dir to corrected sinogram
    output_base = os.path.join(recons_dir, "stir_sinogram_corrected")

    #Save .hdr and .img
    nib.save(corrected_img, output_base)

    #Copy .img to .s
    img_file = output_base + ".img"
    s_file = output_base + ".s"
    shutil.copy(img_file, s_file)

    #Copy file strir_sinogram.hs
    stir_sinogram_hs = stir_sino_path + ".hs"
    hs_file_new = output_base + ".hs"
    shutil.copy(stir_sinogram_hs, hs_file_new)
    
    #Open hs_file_new to modify
    with open(hs_file_new, 'r') as f:
        lines = f.readlines()
    
    #Modify line where appear stir_sinogram.s to stir_sinogram_corrected.s
    lines = [line.replace("stir_sinogram.s", "stir_sinogram_corrected.s") for line in lines]

    #Save changes
    with open(hs_file_new, 'w') as f:
        f.writelines(lines)

    return (hs_file_new)
