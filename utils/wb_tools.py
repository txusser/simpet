from os.path import join, exists, isdir, dirname, basename, split
import os
import nibabel as nib
import numpy as np
import yaml
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
from utils import tools
from utils import resources as rsc

change_format = rsc.get_rsc('change_format', 'fruitcake')

def calculate_center_slices(act_map,scanner,zmin,zmax,overlapping=0.1):

    
    act_img = nib.load(act_map)
    z_voxsize = act_img.affine[2,2]

    z_nvoxels = zmax-zmin

    act_z_length = z_nvoxels*z_voxsize
    
    eff_aFOV = scanner.get("axial_fov")*10*(1-2*overlapping)

    beds_cs = []
    voxels_per_bed = eff_aFOV/z_voxsize
    bed_0_center = zmin + np.rint(voxels_per_bed/2)
    beds_cs.append(bed_0_center)

    bed_center = bed_0_center

    while bed_center<zmax-voxels_per_bed:
        bed_center = np.rint(bed_center + voxels_per_bed)
        beds_cs.append(bed_center)
    
    return beds_cs

def join_beds_wb(recons_beds,joint_beds):

    bed_0 = nib.load(recons_beds[0])
    bed_0_data = tools.fix_4d_data(bed_0.get_fdata())

    num_slices = bed_0_data.shape[2]
    slices_to_remove = int(np.rint(num_slices/10))

    bed_0_data = bed_0_data[:,:,:-slices_to_remove]

    if len(recons_beds)>2:
        for i in range(1,len(recons_beds)-1):
            print(i)

            bed = nib.load(recons_beds[i])
            bed_data = tools.fix_4d_data(bed.get_fdata())
            bed_data = bed_data[:,:,slices_to_remove:-slices_to_remove]
            bed_0_data = np.append(bed_0_data,bed_data, axis=2)

    bed_last = nib.load(recons_beds[-1])
    bed_data = tools.fix_4d_data(bed_last.get_fdata())
    bed_data = bed_data[:,:,slices_to_remove:]
    bed_0_data = np.append(bed_0_data,bed_data, axis=2)


    bed_0_data = np.flipud(bed_0_data)
    bed_0_data = np.fliplr(bed_0_data)

    hdr1 = nib.AnalyzeHeader()
    dtype = bed_0.get_data_dtype()  
    hdr1.set_data_dtype(dtype)
    hdr1.set_data_shape(bed_0_data.shape)
    affine = bed_0.affine
    print(affine)
    hdr1.set_zooms((abs(affine[0,0]),abs(affine[1,1]),abs(affine[2,2])))

    analyze_img = nib.AnalyzeImage(bed_0_data, hdr1.get_base_affine(), hdr1)
    nib.save(analyze_img,joint_beds)

def cut_image_min_max_slices(input_img, min_slice, max_slice, output):

    img = nib.load(input_img)
    img_data = tools.fix_4d_data(img.get_fdata())

    img_data = img_data[:,:,min_slice:max_slice]

    hdr1 = nib.AnalyzeHeader()
    dtype = img.get_data_dtype()  
    hdr1.set_data_dtype(dtype)
    hdr1.set_data_shape(img_data.shape)
    affine = img.get_affine()
    hdr1.set_zooms((abs(affine[0,0]),abs(affine[1,1]),abs(affine[2,2])))

    analyze_img = nib.AnalyzeImage(img_data, hdr1.get_base_affine(), hdr1)
    nib.save(analyze_img,output)

    return output




