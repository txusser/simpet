
import sys
import math  #new
from os.path import join, dirname
import nibabel as nib
import numpy as np
import os
from scipy.ndimage import zoom
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
from pyprojroot import here

sys.path.append(str(here()))
from utils import resources as rsc
from utils import spm_tools as spm
from utils import tools
from src.stir import stir_tools

#Real Distribution
act_map  = 

#Organs diferences for region with differents values
act_map_dif_region = 
#Changed of dimensions
ct_image = join(output_dir, "Ct_image_act.img")
ct_image_2 = join(output_dir, "CT_image_act.img")
#address of map
rec_OSEM3D_48_norm.hdr
rec_OSEM3D_48_norm_wholeBody.hdr

total_quantification = join(output_dir, 'rec_%s_%s_norm.hdr' % (recons_algorithm, recons_it))
quantification_file = join(output_dir, "Quantification_data.txt")
info_act_map = 


def rotate_image(act_map, ct_image_act):
    # Upload original image (corresponding to the activity map)
    act_img = nib.load(act_map)
    #act_data = act_img.get_fdata()
    act_data = act_img.dataobj[:]  # conserva enteros y evita decimales
    

    print(f"Image_before_rotate:{act_img.affine}")

    act_header = act_img.header
    act_shape = np.array(act_data.shape[:3])
    act_voxel_sizes = act_img.header.get_zooms()[:3]

    # Rotation and flip
    rot_xy = np.rot90(act_data, k=2, axes=(0,1))
    final = np.flip(rot_xy, axis=0)
    

    # Save final image 
    final_img = nib.Nifti1Image(final, act_img.affine, act_img.header)
    

    output_base = os.path.splitext(ct_image_act)[0]
    if not output_base.endswith(".img") and not output_base.endswith(".hdr"):
        output_base = output_base  # base name without extension

    output_path = output_base + ".img"  # nibabel will also generate the .hdr
    nib.save(final_img, output_path)

    return final

def change_act_dimensions(ct_image_act_2, ct_image_act, joint_beds):
    """
    Adjust a CT image to match reference voxel size and shape, padding with zeros if necessary.
    """
    # --- Load original image ---
    img = nib.load(ct_image_act)
    data = img.dataobj[:]  # conserva enteros y evita decimales

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


    print("Original Dimensions:", data.shape)
    print("Scale Factor:", scale_factor)
    
    # --- Reescalar volumen (sin interpolación continua) ---
    new_data = zoom(data, zoom=scale_factor, order=0, prefilter=False)

    # --- Corrige origen geométrico para que el centro quede alineado ---
    orig_center = (shape * voxel_size) / 2
    new_center = (new_shape * new_voxel_size) / 2
    shift = orig_center - new_center  # desplazamiento en mm

    # --- Nueva cabecera y affine ---
    new_affine = recons_img.affine.copy()
    new_affine[:3, :3] = np.diag(new_voxel_size)
    new_affine[:3, 3] = 0  # centra la imagen correctamente

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
            # La imagen es más pequeña → agregamos ceros
            pad_width.append((diff[i] // 2, diff[i] - diff[i] // 2))
        else:
            # La imagen es más grande → recortamos
            start = abs(diff[i]) // 2
            end = start + recons_shape[i]
            cropped_data = np.take(cropped_data, indices=range(start, end), axis=i)
            pad_width.append((0, 0))

    padded_data = np.pad(final_image.get_fdata(), pad_width, mode='constant', constant_values=0)
    
    #  --- Ajuste final de tamaño exacto ---
    # En algunos casos, el padding o recorte previo deja 1 voxel de diferencia por redondeos
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
    nib.save(final_padded_image, ct_image_act_2)
    
    # --- Delete original image ---
    base_name = os.path.splitext(ct_image_act)[0]  # quita la extensión .img
    for f in [base_name + ".img", base_name + ".hdr"]:
        if os.path.exists(f):
            os.remove(f)
        
    return final_padded_image

def total_quantification(ct_image_act_2, joint_norm_beds, quantification_file):
    """
    Compute information of target image per labeled region in reference image and save to a TXT file.
    Obtains information about the simulated distribution of activity in the phantom and saves it in a TXT file.
    """
    # --- Load images ---
    target_img = nib.load(joint_norm_beds)
    roi_img = nib.load(ct_image_act_2)
    
    
    target_data = target_img.get_fdata()
    roi_data = roi_img.get_fdata()

    
    # --- Ensure same shape ---
    if target_data.shape != roi_data.shape:
        raise ValueError("Target and reference images must have the same shape.")
    
    # --- Get all labels except 0 (background) ---
    labels = np.unique(roi_data)
    labels = labels[labels != 0]
    
    # --- Calculate mean per label ---
    mean_values = [target_data[roi_data == label].mean() for label in labels]  #KBq/cc

    #--- Calculate Volumen per label ---
    voxel_counts = [np.sum(roi_data == label) for label in labels]
    dx, dy, dz = np.array(roi_img.header.get_zooms()[:3])
    voxel_volume = dx * dy * dz

    volumes = [(count * voxel_volume)/1000 for count in voxel_counts]

    # --- Calculate activity per region ---
    activity_region_KBq = [m * v for m, v in zip(mean_values, volumes)]
    activity_region_mCi = [a / (3.7 * 10**4) for a in activity_region_KBq]
    mean_values_mCi = [b / c for b, c in zip(activity_region_mCi, volumes)]

    #  --- Calculate TOTAL activity across all labels ---
    total_activity_KBq = float(np.sum(activity_region_KBq))
    total_activity_mCi = float(np.sum(activity_region_mCi))

    # --- Save report as TXT ---
    with open(quantification_file, 'w') as f:
        # Encabezado
        f.write(
            f"{'Label':<10}{'MeanValue (mCi/cc)':>20}{'MeanValue (KBq/cc)':>20}{'Pixels':>15}"
            f"{'Vol (ccm³)':>15}{'Act (mCi)':>15}{'Act (KBq)':>15}\n"
        )
        
        # Filas por cada label
        for label, mean_val_mCi, mean_val_KBq, count, vol, act_mCi, act_KBq in zip(
            labels, mean_values_mCi, mean_values, voxel_counts, volumes, activity_region_mCi, activity_region_KBq
        ):
            f.write(
                f"{int(label):<10}{mean_val_mCi:>20.4f}{mean_val_KBq:>20.4f}{count:>15.0f}"
                f"{vol:>15.4f}{act_mCi:>15.4f}{act_KBq:>15.4f}\n"
                )
        # Linea separadora
        f.write("="*90 + "\n")
         
        # Linea TOTAL
        f.write(
            f"{'TOTAL':<10}{'':>20}{'':>15}{'':>15}"
            f"{total_activity_mCi:>15.4f}{total_activity_KBq:>15.4f}\n"
        )

    return {"labels": labels, "mean_values_mCi": mean_values_mCi, "mean_values_KBq": mean_values, "pixel_counts": voxel_counts,
    "volumes": volumes, "activity_mCi": activity_region_mCi, "activity_KBq": activity_region_KBq,
    "total_activity_mCi": total_activity_mCi, "total_activity_KBq": total_activity_KBq
    }


    """
    Compute information of target image per labeled region in reference image and save to a TXT file.
    Obtains information about the simulated distribution of activity in the phantom and saves it in a TXT file.
    """
    # --- Load images ---
    target_img = nib.load(recons_norm_wholeBody_file)
    roi_img = nib.load(ct_image_act_2)
    
    
    target_data = target_img.get_fdata()
    roi_data = roi_img.get_fdata()

    
    # --- Ensure same shape ---
    if target_data.shape != roi_data.shape:
        raise ValueError("Target and reference images must have the same shape.")
    
    # --- Get all labels except 0 (background) ---
    labels = np.unique(roi_data)
    labels = labels[labels != 0]
    
    # --- Calculate mean per label ---
    mean_values_KBq = [target_data[roi_data == label].mean() for label in labels]
    mean_values_mCi = mean_values_mCi = [v * 0.00002703 for v in mean_values_KBq]   #mCi

    #--- Calculate Volumen per label ---
    voxel_counts = [np.sum(roi_data == label) for label in labels]
    dx, dy, dz = np.array(roi_img.header.get_zooms()[:3])
    voxel_volume = dx * dy * dz

    volumes = [(count * voxel_volume)/1000 for count in voxel_counts]

    # --- Calculate activity per region ---
    activity_region_KBq = [m * v for m, v in zip(mean_values_KBq, volumes)]
    activity_region_mCi = [a / (3.7 * 10**4) for a in activity_region_KBq]

    #  --- Calculate TOTAL activity across all labels ---
    total_activity_KBq = float(np.sum(activity_region_KBq))
    total_activity_mCi = float(np.sum(activity_region_mCi))

    

    # --- Save report as TXT ---
    with open(quantification_file, 'w') as f:
        # Encabezado
        f.write(
            f"{'Label':<10}{'MeanValue (mCi/cc)':>20}{'MeanValue (KBq/cc)':>20}{'Pixels':>15}"
            f"{'Vol (ccm³)':>15}{'Act (mCi)':>15}{'Act (KBq)':>15}\n"
        )
        
        # Filas por cada label
        for label, mean_val_mCi, mean_val_KBq, count, vol, act_mCi, act_KBq in zip(
            labels,mean_values_KBq, mean_values_mCi, voxel_counts, volumes, activity_region_mCi, activity_region_KBq
        ):
            f.write(
                f"{int(label):<10}{mean_val_mCi:>20.4f}{mean_val_KBq:>20.4f}{count:>15.0f}"
                f"{vol:>15.4f}{act_mCi:>15.4f}{act_KBq:>15.4f}\n"
                )
        # Linea separadora
        f.write("="*90 + "\n")
         
        # Linea TOTAL
        f.write(
            f"{'TOTAL':<10}{'':>20}{'':>15}{'':>15}"
            f"{total_activity_mCi:>15.4f}{total_activity_KBq:>15.4f}\n"
        )


    return {"labels": labels, "mean_values_mCi": mean_values_mCi, "mean_values_KBq": mean_values_mCi, "pixel_counts": voxel_counts,
    "volumes": volumes, "activity_mCi": activity_region_mCi, "activity_KBq": activity_region_KBq,
    "total_activity_mCi": total_activity_mCi, "total_activity_KBq": total_activity_KBq 
    }

def distribution_of_dose_into_phantom(act_map, info_act_map, self):
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
        print(f"phantom_dose: {phantom_dose} au")

        act_table_factor = self.sim_dose * 1000 / phantom_dose
    else:
        act_table_factor = 1
    
    print(f"Factor_actividad: {act_table_factor}")
    print(f"self.sim_dose: {self.sim_dose} mCi")
    print(f"total_phantom_counts: {total_phantom_counts}")

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

    
    # Get information about the new image

    # --- Calculate average values per label ---
    labels = np.unique(phantom_act_data)
    labels = labels[labels != 0]

    mean_values_mCi = [phantom_real_act[phantom_act_data == label].mean() for label in labels]
    voxel_counts = [np.sum(phantom_act_data == label) for label in labels]
    volumes_region = [count * phantom_voxel_volumen for count in voxel_counts]
    
    print(f"voxel_counts: {voxel_counts}")
    print(f"volumes_region: {volumes_region}")
    print(f"phantom_volumen_voxel:{phantom_voxel_volumen}")

    # --- Calculate activity per region ---
    activity_region_mCi = [m * v for m, v in zip(mean_values_mCi, volumes_region)]
    activity_region_KBq = [a * 3.7 * 10**4 for a in activity_region_mCi]
    mean_values_KBq = [b / c for b, c in zip(activity_region_KBq , volumes_region)]

    #  --- Calculate TOTAL activity across all labels ---
    total_activity_KBq = float(np.sum(activity_region_KBq))
    total_activity_mCi = float(np.sum(activity_region_mCi))
    
    print(f"activity_region_KBq: {activity_region_KBq}")
    # --- Save report as TXT ---

    with open(info_act_map, 'w') as f:
        f.write(f"{'Label':<10}{'MeanValue (mCi/cc)':>20}{'MeanValue (KBq/cc)':>20}{'Pixels':>15}{'Vol (ccm³)':>15}{'Act (mCi)':>15}{'Act (KBq)':>15}\n")
        for label, mean_val_mCi, mean_val_KBq, count, vol, act_mCi, act_KBq in zip(
            labels, mean_values_mCi, mean_values_KBq, voxel_counts, volumes_region, activity_region_mCi, activity_region_KBq
        ):
            f.write(f"{int(label):<10}{mean_val_mCi:>20.4f}{mean_val_KBq:>20.4f}{count:>15.0f}{vol:>15.4f}{act_mCi:>15.4f}{act_KBq:>15.4f}\n")
    

    # Linea separadora
        f.write("="*90 + "\n")
         
        # Linea TOTAL
        f.write(
            f"{'TOTAL':<10}{'':>20}{'':>15}{'':>15}"
            f"{total_activity_mCi:>15.4f}{total_activity_KBq:>15.4f}\n"
        )

    return {
        "image_path": output_path, "factor": act_table_factor,
        "labels": labels, "mean_values_mCi": mean_values_mCi,"mean_values_KBq": mean_values_KBq,"volumes":  volumes_region,
        "activity_mCi": act_mCi, "activity_KBq": act_KBq, "total_activity_mCi": total_activity_mCi, "total_activity_KBq": total_activity_KBq
        }
