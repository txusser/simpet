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

def create_analyze_from_imgdata(data, out, pix_x, pix_y, pix_z, tx, ty, tz, data_type="fl"):

    if data_type == "1b":
        dtype=np.int8
    elif data_type == "2b":
        dtype=np.int16
    elif data_type == "db":
        dtype=np.float64
    else:
        dtype=np.float32
   
    hdr1 = nib.AnalyzeHeader()
    hdr1.set_data_dtype(dtype)
    hdr1.set_data_shape((pix_x,pix_y,pix_z))
    hdr1.set_zooms((tx,ty,tz))

    img_data = hdr1.raw_data_from_fileobj(data)

    analyze_img = nib.AnalyzeImage(img_data, hdr1.get_base_affine(), hdr1)

    nib.save(analyze_img,out)

def read_analyze_header(header_file,logfile):

    img = nib.load(header_file)

    zpix = img.shape[2]
    zsize = abs(img.get_affine[2,2])
    xpix = img.shape[0]
    xsize = abs(img.get_affine[0,0])
    ypix = img.shape[1]
    ysize = abs(img.get_affine[1,1])

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

def operate_images_analyze(image1, image2, out_image, operation='mult', ):
    """
    Given the input images, calculate the multiplication image or the ratio between them
    :param image1: string, path to the first image
    :param image2: string, path to the second image
    :param operation: string, multi (default) for multiplication divid for division
    :param out_image: string (optional), path to the output image
    :return: 
    """
    img1, data1 = nib_load(image1)
    img2, data2 = nib_load(image2)

    # TODO CHECK IF NEGATIVE VALUES NEED TO BE REMOVED
    # Remove NaN and negative values
    data1 = np.nan_to_num(data1)
    data2 = np.nan_to_num(data2)

    if operation == 'mult':
        res_data = data1 * data2
    elif operation == 'div':
        res_data = data1 / data2
    elif operation == 'sum':
        res_data = data1 + data2
    elif operation == 'diff':
        res_data = data1 - data2
    else:
        message = 'Error! Unknown operation: ' + str(operation)
        raise TypeError(message)

    hdr1 = nib.AnalyzeHeader()
    hdr1.set_data_dtype(img1.get_data_dtype())
    hdr1.set_data_shape(img1.get_shape())
    hdr1.set_zooms(abs(np.diag(img1.affine))[0:3])
        
    analyze_img = nib.AnalyzeImage(res_data, hdr1.get_base_affine(), hdr1)

    nib.save(analyze_img,out_image)
    
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

def petmr2maps(pet_image,mri_image,log_file,mode="SimSET"):
        """
        It will create act and att maps from PET and MR images.
        Required inputs are:
        pet_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mri_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mode: Choose STIR or SIMSET. The maps will be different for each simulation.
        The inputs will be stored to Data/simulation_name/Patient as reformatted/corregistered Analyze
        The maps will be stored on Data/simulation_name/Maps
        """
        message = "GENERATING ACT AND ATT MAPS FROM PETMR IMAGES"
        tools.log_message(log_file, message, mode='info')

        #First of all lets take all to analyze
        pet_hdr = tools.anything_to_hdr_convert(pet_image)
        pet_hdr = tools.copy_analyze(pet_hdr,image2=False,dest_dir=self.patient_dir)
        pet_hdr = tools.prepare_input_image(pet_hdr,log_file,min_voxel_size=1.5)
        pet_img = pet_hdr[0:-3]+"img"

        mri_hdr = tools.anything_to_hdr_convert(mri_image)
        mri_hdr = tools.copy_analyze(mri_hdr,image2=False,dest_dir=self.patient_dir)
        mri_hdr = tools.prepare_input_image(mri_hdr,log_file,min_voxel_size=1.5)
        mri_img = mri_hdr[0:-3]+"img"

        #Performing PET/MR coregister
        mfile = os.path.join(self.patient_dir,"fusion.m")
        correg_pet_img = tools.image_fusion(self.spm_run, mfile, mri_img, pet_img, log_file)

        #Now the map generation
        from src.patient2maps import patient2maps

        my_map_generation = patient2maps(self.spm_run, self.sim_maps_dir, log_file,
                                         mri_img, correg_pet_img, mode=mode)
        activity_map_hdr, attenuation_map_hdr = my_map_generation.run()

        return activity_map_hdr, attenuation_map_hdr

def convert_map_values(act_map,att_map,output_dir,log_file,mode="SimSET"):

        message = "CONVERTING ACT AND ATT TO %s" % mode
        log_message(log_file, message, mode='info')

        act_map = anything_to_hdr_convert(act_map)
        att_map = anything_to_hdr_convert(att_map)

        cambia_formato = rsc.get_rsc('change_format', 'fruitcake')
        cambia_val = rsc.get_rsc('change_values', 'fruitcake')

        new_att_map = join(output_dir, "att_map_" + mode +".hdr")
        new_act_map = join(output_dir,"act_map_" + mode +".hdr")

        if mode == "SimSET":

            rcommand = '%s %s %s 0.096 1 >> %s' % (cambia_val, att_map, new_att_map, log_file)
            osrun(rcommand, log_file)
            rcommand = '%s %s %s 0.135 3 >> %s' % (cambia_val, new_att_map, new_att_map, log_file)
            osrun(rcommand, log_file)
            rcommand = '%s %s %s 1B >> %s' % (cambia_formato, new_att_map, new_att_map, log_file)
            osrun(rcommand, log_file)
            rcommand = '%s %s %s 1B >> %s' % (cambia_formato, act_map, new_act_map, log_file)
            osrun(rcommand, log_file)

        if mode == "STIR":

            rcommand = '%s %s %s fl >> %s' % (cambia_formato, att_map, new_att_map, log_file)
            osrun(rcommand, log_file)
            rcommand = '%s %s %s fl >> %s' % (cambia_formato, new_act_map, new_act_map, log_file)
            osrun(rcommand, log_file)
            rcommand = '%s %s %s 1  0.096 >> %s' % (cambia_val, new_att_map, new_att_map, log_file)
            osrun(rcommand, log_file)
            rcommand = '%s %s %s 3  0.135 >> %s' % (cambia_val, new_att_map, new_att_map, log_file)
            osrun(rcommand, log_file)

        return new_act_map, new_att_map

def ncounts(image_hdr):

    img, data = nib_load(image_hdr)
    ncounts = np.sum(data)
    return ncounts

