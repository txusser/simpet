import os,shutil, datetime
from os.path import join, exists, isfile, isdir, dirname, basename, splitext
from commands import getstatusoutput as getoutput
import nibabel as nib
from utils import resources as rsc
import numpy as np

def osrun(command, logfile, catch_out=False):
    """
    Executes command, raise an error if it fails and send status to logger
    :param command: command to be executed
    :param logger: logger file
    :return:
    """
    if catch_out:
        status, out = getoutput(command)
        if status != 0:
            log_message(logfile, command, 'error')
            raise TypeError(command)
        else:
            log_message(logfile, command)
        return out

    else:
        if os.system(command) != 0:

            log_message(logfile, command, 'error')
            raise TypeError(command)
        else:
            log_message(logfile, command)

def nib_load(image, logfile=False):
    """
    Load image and return data array
    :param image: image to load data from
    :return: image data array
    """
    try:
        img = nib.load(image)
        data = img.get_data()[:,:,:]
        return img, data
    except Exception as e:
        message = "Error: " + str(e)
        if logfile:
            log_message(logfile, message, 'error')
        else:
            print message

def copy_analyze(image1, image2=False, dest_dir=False, logfile=False):
    """
    Create a copy of an Analyze format image
    :param image1: (string) path to the original image
    :param image2: (string, optional) path to the copy image
    :param dest_dir: (string, optional) path to the destination folder
    :return:
    """

    if image2:
        if image1[-3:] == 'hdr' or image1[-3:] == 'img' and image2[-3:] == 'hdr' or image2[-3:] == 'img':
            image1_hdr = image1[0:-3] + 'hdr'
            image2_hdr = image2[0:-3] + 'hdr'
            shutil.copy(image1_hdr, image2_hdr)
            image1_img = image1[0:-3] + 'img'
            image2_img = image2[0:-3] + 'img'
            shutil.copy(image1_img, image2_img)

            return image2_hdr
        else:
            message = 'Error! The provided image is not in Analyze format:' + str(image1)
            if logfile: log_message(logfile, message, 'error')
            raise TypeError(message)

    elif not image2 and isdir(str(dest_dir)):

        ext = splitext(basename(image1))[1]

        if ext == '.img' or ext == '.hdr':
            image1_hdr = image1[0:-3] + 'hdr'
            image2_hdr = join(dest_dir, basename(image1)[0:-3] + 'hdr')
            shutil.copy(image1_hdr, image2_hdr)
            image1_img = image1[0:-3] + 'img'
            image2_img = join(dest_dir, basename(image1)[0:-3] + 'img')
            shutil.copy(image1_img, image2_img)

            return  image2_hdr
        else:
            message = 'Error! The provided image is not in Analyze format:' + str(image1)
            if logfile: log_message(logfile, message, 'error')
            raise TypeError(message)
    else:
        message = 'Error! Not image2 path or dest dir path provided: ' + str(image2) + ', ' + str(dest_dir)
        if logfile: log_message(logfile, message, 'error')
        raise TypeError(message)

def read_analyze_header(header_file,logfile):

    rcommand = 'printf_header_hdr %s' % header_file
    header = osrun(rcommand, logfile,catch_out=True)

    zpix = int(header.split()[13])
    zsize = float(header.split()[31])
    xpix = int(header.split()[19])
    xsize = float(header.split()[37])
    ypix = int(header.split()[25])
    ysize = float(header.split()[43])

    return zpix, zsize, xpix, xsize, ypix, ysize

def write_interfile_header(header_file,matrix_size_x,pixel_size_x,
                matrix_size_y,pixel_size_y,
                matrix_size_z,pixel_size_z):

    image_v = os.path.basename(header_file)[0:-2] + "v"
    fheader_hv = open(header_file, "w")

    offset_x = matrix_size_x/2*pixel_size_x
    offset_y = matrix_size_y/2*pixel_size_y

    fheader_hv.write("!INTERFILE  :=\n")
    fheader_hv.write("name of data file := %s\n" % image_v)
    fheader_hv.write("!GENERAL DATA :=\n")
    fheader_hv.write("!GENERAL IMAGE DATA :=\n")
    fheader_hv.write("!type of data := PET\n")
    fheader_hv.write("imagedata byte order := LITTLEENDIAN\n")
    fheader_hv.write("!PET STUDY (General) :=\n")
    fheader_hv.write("!PET data type := Image\n")
    fheader_hv.write("process status := Reconstructed\n")
    fheader_hv.write("!number format := float\n")
    fheader_hv.write("!number of bytes per pixel := 4\n")
    fheader_hv.write("number of dimensions := 3\n")
    fheader_hv.write("matrix axis label [1] := x\n")
    fheader_hv.write("!matrix size [1] := %s\n" % matrix_size_x)
    fheader_hv.write("scaling factor (mm/pixel) [1] := %s\n" % pixel_size_x)
    fheader_hv.write("matrix axis label [2] := y\n")
    fheader_hv.write("!matrix size [2] := %s\n" % matrix_size_y)
    fheader_hv.write("scaling factor (mm/pixel) [2] := %s\n" % pixel_size_y)
    fheader_hv.write("matrix axis label [3] := z\n")
    fheader_hv.write("!matrix size [3] := %s\n" % matrix_size_z)
    fheader_hv.write("scaling factor (mm/pixel) [3] := %s\n" % pixel_size_z)
    fheader_hv.write("first pixel offset (mm) [1] := -%s\n" % offset_x)
    fheader_hv.write("first pixel offset (mm) [2] := -%s\n" % offset_y)
    fheader_hv.write("first pixel offset (mm) [3] := 0\n")
    fheader_hv.write("number of time frames := 1\n")
    fheader_hv.write("!END OF INTERFILE :=\n")

    fheader_hv.close()

def nii_analyze_convert(image, logfile=False, outfile=False):
    """
    Converts the provided image file to the analyze or nifti format
    depending on the filex extension
    :param image: image to be converted
    :return:
    """

    if not logfile: logfile = join(dirname(image), 'log_nii_analyze_convert.txt')

    ext = os.path.splitext(image)[1]

    if ext == '.nii':
        n2a =  rsc.get_rsc('nii2analyze', 'exe')
        if outfile:
            cimage = outfile
        else:
            cimage = image.replace('.nii', '.hdr')
        rcommand = '%s %s %s >> %s' % (n2a, image, cimage, logfile)
        osrun(rcommand, logfile)
    elif ext == '.hdr':
        a2n =  rsc.get_rsc('analyze2nii', 'exe')
        if outfile:
            cimage = outfile
        else:
            cimage = image.replace('.hdr', '.nii')
        rcommand = '%s %s %s >> %s' % (a2n, image, cimage, logfile)
        osrun(rcommand, logfile)
    else:
        a2n =  rsc.get_rsc('analyze2nii', 'exe')
        if outfile:
            cimage = outfile
        else:
            cimage = image.replace('.img', '.nii')
        image_hdr = str(image).replace(".img", ".hdr")
        rcommand = '%s %s %s >> %s' % (a2n, image_hdr, cimage, logfile)
        osrun(rcommand, logfile)

    if exists(cimage):
        if outfile:
            shutil.move(cimage, outfile)
            return outfile
        else:
            return cimage
    else:
        return 0

def anything_to_hdr_convert(image, logfile=False, outfile=False ):
    """
    This function will try to convert dicom, .nii.gz or .nii to analyze...
    """

    if image[-3:] == "hdr" or image[-3:] == "img":
        return image[0:-3]+"hdr"

    elif image[-3:] == "nii":
        hdr = nii_analyze_convert(image,logfile=logfile)
        if exists(hdr):
            return hdr
        else:
            raise TypeError ("nifti-analyze conversion failed....")

    elif image[-6:]=="nii.gz":
        rcommand= 'gunzip %s' % image
        nii = image[-6:-3]
        if exists(nii):
            hdr = ap.nii_analyze_convert(nii,logfile=logfile)
            os.remove(nii)
            if exists(hdr):
                return hdr
            else:
                raise TypeError ("nifti-analyze conversion failed....")
        else:
            raise TypeError ("dicom-nifti conversion failed....")

    elif isdir(image):
        print("I think the provided image:\n %s \n is a dicom directory. I will try to convert it...")
        dicom2nii = rsc.get_rsc("dicom2nii","exe")
        nii = join(self.patient_dir,"image.nii")
        rcommand = '%s %s %s' % (dicom2nii, image, nii)
        osrun(rcommand,logfile)
        if exists(nii):
            hdr = ap.nii_analyze_convert(nii,logfile=logfile)
            os.remove(nii)
            if exists(hdr):
                return hdr
            else:
                raise TypeError ("nifti-analyze conversion failed....")
        else:
            raise TypeError ("dicom-nifti conversion failed....")

    elif image[-2:] == "hv": #Only works with floats data

        with open(image) as f:
            lines = f.readlines()

        lines = [x.strip() for x in lines]

        pixel_x = lines[13].split()[4]
        pixel_size_x = lines[14].split()[5]
        pixel_y = lines[16].split()[4]
        pixel_size_y = lines[17].split()[5]
        pixel_z = lines[19].split()[4]
        pixel_size_z = lines[20].split()[5]

        hdr_header = image[0:-2] + "hdr"
        img_file = image[0:-2] + "img"
        data_file = image[0:-2] + "v"

        #This will convert .hv to .hdr and copy the data
        os.system("gen_hdr %s %s %s %s fl %s %s %s 0" % (hdr_header, pixel_x, pixel_y, pixel_z, pixel_size_x, pixel_size_y, pixel_size_z))
        shutil.copy(data_file, img_file)

        if exists(hdr_header):
            return hdr_header
        else:
            raise TypeError ("Interfile-analyze conversion failed....")

def prepare_input_image(image_hdr, logfile, min_voxel_size=1):
    """
    This method converts input_image to float data type, re-sizes the image to
    1mm size voxels if too large to keep a reasonable analysis execution time and
    removes the negative and NaN values.
    :param input_image: image to prepare for the analysis
    :return:
    """

    # Tools for image manipulation
    change_format = rsc.get_rsc('change_format', 'fruitcake')
    change_matrix = rsc.get_rsc('change_img_matrix', 'fruitcake')
    erase_negs = rsc.get_rsc('erase_negs', 'fruitcake')
    erase_nans = rsc.get_rsc('erase_nans', 'fruitcake')

    # Convert input image to Analyze format and float data type
    rcommand = '%s %s %s fl >> %s' % (change_format, image_hdr, image_hdr, logfile)
    osrun(rcommand, logfile)

    # Resize image if necessary
    ndims = recalculate_matrix(image_hdr, min_voxel_size)
    rcommand = '%s %s %s %s %s %s novecino >> %s' % (change_matrix, image_hdr, image_hdr,
                                                     str(ndims[0]), str(ndims[1]), str(ndims[2]), logfile)
    osrun(rcommand, logfile)

    # Erase negative and NaN values
    rcommand = '%s %s %s >> %s' % (erase_negs, image_hdr, image_hdr, logfile)
    osrun(rcommand, logfile)
    rcommand = '%s %s %s >> %s' % (erase_nans, image_hdr, image_hdr, logfile)
    osrun(rcommand, logfile)

    return image_hdr

def recalculate_matrix(input_image, voxelsize, mode="downsampling"):

    new_dimensions = []
    image_load, data = nib_load(input_image)
    header = image_load.header
    sizes = header.get_zooms()
    dimensions = image_load.get_shape()
    x_lenght = int(sizes[0]*dimensions[0]/voxelsize)
    y_lenght = int(sizes[1]*dimensions[1]/voxelsize)
    z_lenght = int(sizes[2]*dimensions[2]/voxelsize)
    if mode == "downsampling":
        if sizes[0]<voxelsize:
            new_dimensions.append(x_lenght)
        else:
            new_dimensions.append(dimensions[0])
        if sizes[1]<voxelsize:
            new_dimensions.append(y_lenght)
        else:
            new_dimensions.append(dimensions[1])
        if sizes[2]<voxelsize:
            new_dimensions.append(z_lenght)
        else:
            new_dimensions.append(dimensions[2])
    if mode == "supersampling":
        if sizes[0]>voxelsize:
            new_dimensions.append(x_lenght)
        else:
            new_dimensions.append(dimensions[0])
        if sizes[1]>voxelsize:
            new_dimensions.append(y_lenght)
        else:
            new_dimensions.append(dimensions[1])
        if sizes[2]>voxelsize:
            new_dimensions.append(z_lenght)
        else:
            new_dimensions.append(dimensions[2])

    return new_dimensions

def verify_roi_exists(rois_image, roi_number):
    """
    Compute the number of voxels in each ROI
    :param rois_image: (string) path to the ROI parcelled image
    :param rois_list: (array) ROIs indexing
    :return: False if the number of voxels is zero
    :return: nvox is not zero
    """
    rois_img = nib.load(rois_image)
    rois_data = rois_img.get_data()[:, :, :]
    indx = np.where(rois_data == roi_number)
    nvox = len(rois_data[indx])
    if nvox == 0:
        return False
    else:
        return True

def operate_single_image(input_image, operation, factor, output_image, logfile):
    """
    Given an input image, multiply or divide it by a numerical factor
    saving the result as output_image
    :param input_image: image base operation on
    :param operation: 1 = multiply, 2 = divide
    :param factor: operation factor
    :param output_image: output image file
    :return:
    """
    try:
        img = nib.load(input_image)
        data = img.get_data()[:,:,:]
        data = np.nan_to_num(data)

        if operation == 'mult':
            data = data * float(factor)
        elif operation == 'div':
            data = data / float(factor)
        else:
            message = "Error! Invalid operation: " +str(operation)
            print message
            log_message(logfile, message, 'error')

        affine = img.affine
        header = img.header
        img = nib.Nifti1Image(data, affine, header)
        nib.save(img, output_image)

        if os.path.exists(output_image):
            message = 'Created image: ' + str(output_image)
            log_message(logfile, message)
        else:
            message = 'Error! Could not create image: ' + str(output_image)
            raise TypeError(message)

    except Exception as e:
        print "Error:", e

def old_normalize(matlab_rcommand, mfile_name, image_to_norm, template_image,  log_file,
                  images_to_write=False, cutoff=15, nits=16, reg=1, preserve=0,
                  affine_regularization_type='mni', source_image_smoothing=8, template_image_smoothing=3,
                  bb=[-78, -112, -70, 78, 76, 85], write_vox_size='[1 1 1]',
                  wrapping=True, interpolation=4, prefix='w'):

    design_type = "matlabbatch{1}.spm.tools.oldnorm.estwrite."

    if not images_to_write:
        images_to_write = [image_to_norm]

    new_spm = open(mfile_name, "a")

    new_spm.write(
        design_type + "subj.source = {'" + image_to_norm + ",1'};" + "\n" +
        design_type + "subj.wtsrc = '';" + "\n" +
        design_type + "subj.resample = {"
        )

    for image in images_to_write:
        new_spm.write("'" + image + ",1'" + "\n")
    new_spm.write("};" + "\n")

    new_spm.write(
        design_type + "eoptions.template = {'" + template_image + ",1'};" + "\n" +
        design_type + "eoptions.weight = '';" + "\n" +
        design_type + "eoptions.smosrc =" + str(source_image_smoothing) + ";" + "\n" +
        design_type + "eoptions.smoref =" + str(template_image_smoothing) + ";" + "\n" +
        design_type + "eoptions.regtype ='" + affine_regularization_type + "';" + "\n" +
        design_type + "eoptions.cutoff =" + str(cutoff) + ";" + "\n" +
        design_type + "eoptions.nits =" + str(nits) + ";" + "\n" +
        design_type + "eoptions.reg =" + str(reg) + ";" + "\n" +
        design_type + "roptions.preserve =" + str(preserve) + ";" + "\n" +
        design_type + "roptions.bb =[" + str(bb[0]) + " " + str(bb[1]) + " " + str(bb[2]) + "\n" +
                                         str(bb[3]) + " " + str(bb[4]) + " " + str(bb[5]) + "];" + "\n" +
        design_type + "roptions.vox =" + write_vox_size + ";" + "\n" +
        design_type + "roptions.interp =" + str(interpolation) + ";" + "\n")

    if wrapping:
        new_spm.write(design_type + "roptions.wrap = [1 1 1];" + "\n")
    else:
        new_spm.write(design_type + "roptions.wrap = [0 0 0];" + "\n")

    new_spm.write(design_type + "roptions.prefix ='" + prefix + "';" + "\n")
    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

    components = os.path.split(images_to_write[0])
    output = os.path.join(components[0], 'w' + components[1])

    transformation_matrix = image_to_norm[0:-4] + "_sn.mat"

    return output, transformation_matrix

def new_normalize(matlab_rcommand, mfile_name, image_to_norm, template_image,  log_file,
                  images_to_write=False, biasreg=0.01, biasfwhm=60, reg="[0 0.001 0.5 0.05 0.2]",
                  affine_regularization_type='mni', fwhm=0, samp=4,
                  bb=[-78, -112, -70, 78, 76, 85], write_vox_size='[1 1 1]', interpolation=4):

    design_type = "matlabbatch{1}.spm.spatial.normalise.estwrite."

    if not images_to_write:
        images_to_write = [image_to_norm]

    new_spm = open(mfile_name, "w")

    new_spm.write(
        design_type + "subj.vol = {'" + image_to_norm + ",1'};" + "\n" +
        design_type + "subj.resample = {"+ "\n"
        )

    for image in images_to_write:
        new_spm.write("'" + image + ",1'" + "\n")
    new_spm.write("};" + "\n")

    new_spm.write(
        design_type + "eoptions.biasreg = " + str(biasreg) + ";" + "\n" +
        design_type + "eoptions.biasfwhm = " + str(biasfwhm) + ";" + "\n" +
        design_type + "eoptions.tpm = {'" + template_image + "'};" + "\n" +
        design_type + "eoptions.affreg = '" + affine_regularization_type + "';" + "\n" +
        design_type + "eoptions.reg = " + reg + ";" + "\n" +
        design_type + "eoptions.fwhm = " + str(fwhm) + ";" + "\n" +
        design_type + "eoptions.samp = " + str(samp) + ";" + "\n" +
        design_type + "woptions.bb = [" + str(bb[0]) + " " + str(bb[1]) + " " + str(bb[2]) + "\n" +
                                          str(bb[3]) + " " + str(bb[4]) + " "+ str(bb[5]) + "];" + "\n" +
        design_type + "woptions.vox = " + write_vox_size + ";" + "\n" +
        design_type + "woptions.interp = " + str(interpolation) + ";" + "\n")

    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

    components = os.path.split(images_to_write[0])
    output = os.path.join(components[0], 'w' + components[1])

    matrix_name = "y_" + os.path.basename(image_to_norm)[0:-3] + "nii"

    transformation_matrix = os.path.join(components[0], matrix_name)

    return output, transformation_matrix

def new_deformations(matlab_rcommand, mfile_name, def_matrix, base_image, images_to_deform,
                     save_dir, interpolation, log_file, mask = 0, fwhm = "[0 0 0]"):

    design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}.inv."
    design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."

    new_spm = open(mfile_name, "w")

    new_spm.write(
        design_type_comp + "comp{1}.def = {'" + def_matrix + "'};" + "\n" +
        design_type_comp + "space = {'" + base_image + "'};" + "\n" +
        design_type_out + "pull.fnames = {"+ "\n"
        )

    for image in images_to_deform:
        new_spm.write("'" + image + "'" + "\n")
    new_spm.write("};" + "\n")

    new_spm.write(
        design_type_out + "pull.savedir.saveusr = {'" + save_dir + "'};" + "\n" +
        design_type_out + "pull.interp =" + str(interpolation) + ";" + "\n" +
        design_type_out + "pull.mask =" + str(mask) + ";" + "\n" +
        design_type_out + "pull.fwhm =" + str(fwhm) + ";" + "\n"
        )

    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

def old_deformations(matlab_rcommand, mfile_name, def_matrix, base_image, images_to_deform,
                     save_dir, interpolation, log_file, mask=1, fwhm ="[0 0 0]"):

    design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}.inv."
    design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."

    new_spm = open(mfile_name, "w")

    new_spm.write(
        design_type_comp + "comp{1}.sn2def.matname = {'" + def_matrix + "'};" + "\n" +
        design_type_comp + "comp{1}.sn2def.vox = [NaN NaN NaN];" + "\n" +
        design_type_comp + "comp{1}.sn2def.bb = [NaN NaN NaN" + "\n" +
        "NaN NaN NaN];" + "\n" +
        design_type_comp + "space = {'" + base_image + "'};" + "\n" +
        design_type_out + "pull.fnames = {" + "\n"
        )

    for image in images_to_deform:
        new_spm.write("'" + image + "'" + "\n")
    new_spm.write("};" + "\n")

    new_spm.write(design_type_out + "pull.savedir.saveusr = {'" + save_dir + "/'};" + "\n" +
        design_type_out + "pull.interp = " + str(interpolation) + ";" + "\n" +
        design_type_out + "pull.mask = " + str(mask) + ";" + "\n" +
        design_type_out + "pull.fwhm = " + str(fwhm) + ";" + "\n"
        )
    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

def smoothing(matlab_rcommand, mfile_name, image_to_smooth, smoothing, prefix, log_file):

    design_type = "matlabbatch{1}.spm.spatial.smooth."
    smoothing_array = "[" + str(smoothing) + " " + str(smoothing) + " " + str(smoothing) + "]"

    new_spm = open(mfile_name, "w")
    new_spm.write(design_type + "data = {'" + image_to_smooth + "'};" + "\n")
    new_spm.write(design_type + "fwhm =" + smoothing_array + ";" + "\n")
    new_spm.write(design_type + "dtype = 0;" + "\n")
    new_spm.write(design_type + "im = 0;" + "\n")
    new_spm.write(design_type + "prefix ='" + prefix + "';" + "\n")
    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

    components = os.path.split(image_to_smooth)
    output = os.path.join(components[0], prefix + components[1])

    return output

def smoothing_xyz(matlab_rcommand, mfile_name, image_to_smooth,
                  smoothing_x, smoothing_y, smoothing_z, prefix, log_file):

    design_type = "matlabbatch{1}.spm.spatial.smooth."
    smoothing_array = "[" + str(smoothing_x) + " " + str(smoothing_y) + " " + str(smoothing_z) + "]"

    new_spm = open(mfile_name, "w")
    new_spm.write(design_type + "data = {'" + image_to_smooth + "'};" + "\n")
    new_spm.write(design_type + "fwhm =" + smoothing_array + ";" + "\n")
    new_spm.write(design_type + "dtype = 0;" + "\n")
    new_spm.write(design_type + "im = 0;" + "\n")
    new_spm.write(design_type + "prefix ='" + prefix + "';" + "\n")
    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

    components = os.path.split(image_to_smooth)
    output = os.path.join(components[0], prefix + components[1])

    return output

def image_fusion(matlab_rcommand, mfile_name, reference_image, source_image, log_file):

    design_type = "matlabbatch{1}.spm.spatial.coreg.estwrite."

    new_spm = open(mfile_name, "w")

    new_spm.write(design_type + "ref = {'" + reference_image + ",1'};" + "\n")
    new_spm.write(design_type + "source = {'" + source_image + ",1'};" + "\n")
    new_spm.write(design_type + "other = {''};" + "\n")
    new_spm.write(design_type + "eoptions.cost_fun = 'nmi';" + "\n")
    new_spm.write(design_type + "eoptions.sep = [4 2];" + "\n")
    new_spm.write(design_type + "eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];" + "\n")
    new_spm.write(design_type + "eoptions.fwhm = [7 7];" + "\n")
    new_spm.write(design_type + "roptions.interp = 4;")
    new_spm.write(design_type + "roptions.wrap = [0 0 0];")
    new_spm.write(design_type + "roptions.mask = 0;")
    new_spm.write(design_type + "roptions.prefix = 'r';")
    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

    components = os.path.split(source_image)
    output = os.path.join(components[0], "r" + components[1])

    return output

def segment_mri_spm(matlab_rcommand, mfile_name, image, template, log_file):

    design_type = "matlabbatch{1}.spm.spatial.preproc."

    new_spm = open(mfile_name, "w")

    new_spm.write(design_type + "channel.vols = {'" + image + ",1'};" + "\n")
    new_spm.write(design_type + "channel.biasreg = 0.001;" + "\n")
    new_spm.write(design_type + "channel.biasfwhm = 60;" + "\n")
    new_spm.write(design_type + "channel.write = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(1).tpm = {'" + template + ",1'};" + "\n")
    new_spm.write(design_type + "tissue(1).ngaus = 1;" + "\n")
    new_spm.write(design_type + "tissue(1).native = [1 0];" + "\n")
    new_spm.write(design_type + "tissue(1).warped = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(2).tpm = {'" + template + ",2'};" + "\n")
    new_spm.write(design_type + "tissue(2).ngaus = 1;" + "\n")
    new_spm.write(design_type + "tissue(2).native = [1 0];" + "\n")
    new_spm.write(design_type + "tissue(2).warped = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(3).tpm = {'" + template + ",3'};" + "\n")
    new_spm.write(design_type + "tissue(3).ngaus = 2;" + "\n")
    new_spm.write(design_type + "tissue(3).native = [1 0];" + "\n")
    new_spm.write(design_type + "tissue(3).warped = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(4).tpm = {'" + template + ",4'};" + "\n")
    new_spm.write(design_type + "tissue(4).ngaus = 3;" + "\n")
    new_spm.write(design_type + "tissue(4).native = [1 0];" + "\n")
    new_spm.write(design_type + "tissue(4).warped = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(5).tpm = {'" + template + ",5'};" + "\n")
    new_spm.write(design_type + "tissue(5).ngaus = 4;" + "\n")
    new_spm.write(design_type + "tissue(5).native = [1 0];" + "\n")
    new_spm.write(design_type + "tissue(5).warped = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(6).tpm = {'" + template + ",6'};" + "\n")
    new_spm.write(design_type + "tissue(6).ngaus = 2;" + "\n")
    new_spm.write(design_type + "tissue(6).native = [0 0];" + "\n")
    new_spm.write(design_type + "tissue(6).warped = [0 0];" + "\n")
    new_spm.write(design_type + "warp.mrf = 1;"+ "\n")
    new_spm.write(design_type + "warp.cleanup = 1;"+ "\n")
    new_spm.write(design_type + "warp.reg = [0 0.001 0.5 0.05 0.2];"+ "\n")
    new_spm.write(design_type + "warp.affreg = 'mni';"+ "\n")
    new_spm.write(design_type + "warp.fwhm = 0;"+ "\n")
    new_spm.write(design_type + "warp.samp = 3;"+ "\n")
    new_spm.write(design_type + "write = [0 0];"+ "\n")
    new_spm.close()

    os.system("%s %s >> %s" % (matlab_rcommand, mfile_name, log_file))

    components = os.path.split(image)
    output_gm = os.path.join(components[0], "c1" + components[1][0:-3]+ "nii")

    return output_gm

def log_message(logfile, message, mode='info'):
    """"
    Print outs logger messages to the specified logfile
    """

    #ctime = read_time(datetime.datetime.now())
    ctime = datetime.datetime.now()

    separator = '\n###########################################################'

    if mode == 'exe':
        stream = separator + '\nTIME: ' + str(ctime) + '\n\nEXE: ' + message + separator + '\n'
    elif mode == 'info':
        stream = separator + '\nTIME: ' + str(ctime) + '\n\nINFO: ' + message + separator + '\n'
    elif mode == 'warning':
        stream = separator + '\nTIME: ' + str(ctime) + '\n\nWARNING: ' + message + separator + '\n'
    elif mode == 'error':
        stream = separator + '\nTIME: ' + str(ctime) + '\n\nERROR: ' + message + separator + '\n'
    else:
        stream = separator + '\nTIME: ' + str(ctime) + '\n\n' + message + '\n'

    if exists(logfile):
        with open(logfile, 'a') as lfile:
            lfile.write(stream)
    else:
        with open(logfile, 'w') as lfile:
            lfile.write(stream)
