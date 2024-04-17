import sys
from os.path import join, dirname
import nibabel as nib
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
from pyprojroot import here

sys.path.append(str(here()))
from utils import resources as rsc
from utils import spm_tools as spm
from utils import tools

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


def calculate_center_slices(act_map, scanner, zmin, zmax, overlapping=0.1):
    act_img = nib.load(act_map)
    z_voxsize = act_img.affine[2, 2]

    z_nvoxels = zmax - zmin

    act_z_length = z_nvoxels * z_voxsize

    eff_aFOV = scanner.get("axial_fov") * 10 * (1 - 2 * overlapping)

    beds_cs = []
    voxels_per_bed = eff_aFOV / z_voxsize
    bed_0_center = zmin + np.rint(voxels_per_bed / 2)
    beds_cs.append(bed_0_center)

    bed_center = bed_0_center

    while (bed_center < zmax - voxels_per_bed):
        bed_center = np.rint(bed_center + voxels_per_bed)
        beds_cs.append(bed_center)

    return beds_cs


def join_beds_wb(recons_beds, joint_beds):
    bed_0 = nib.load(recons_beds[0])
    bed_0_data = tools.fix_4d_data(bed_0.get_fdata())

    num_slices = bed_0_data.shape[2]
    slices_to_remove = int(np.rint(num_slices / 10))

    bed_0_data = bed_0_data[:, :, :-slices_to_remove]

    for i in range(1, len(recons_beds) - 1):
        print(f"Bed: {i}")

        bed = nib.load(recons_beds[i])
        bed_data = tools.fix_4d_data(bed.get_fdata())
        bed_data = bed_data[:, :, slices_to_remove:-slices_to_remove]
        bed_0_data = np.append(bed_0_data, bed_data, axis=2)
    
    bed_last = nib.load(recons_beds[len(recons_beds) - 1])
    bed_data = tools.fix_4d_data(bed_last.get_fdata())
    bed_data = bed_data[:, :, slices_to_remove:]
    bed_0_data = np.append(bed_0_data, bed_data, axis=2)

    bed_0_data = np.flipud(bed_0_data)
    bed_0_data = np.fliplr(bed_0_data)

    hdr1 = nib.AnalyzeHeader()
    dtype = bed_0.get_data_dtype()
    hdr1.set_data_dtype(dtype)
    hdr1.set_data_shape(bed_0_data.shape)
    affine = bed_0.get_affine()
    hdr1.set_zooms((abs(affine[0, 0]), abs(affine[1, 1]), abs(affine[2, 2])))

    analyze_img = nib.AnalyzeImage(bed_0_data, hdr1.get_base_affine(), hdr1)
    nib.save(analyze_img, joint_beds)


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
