import os,shutil, datetime
from os.path import join, exists, isfile, isdir, dirname, basename, splitext
from subprocess import getstatusoutput as getoutput
import nibabel as nib
from utils import resources as rsc
from utils import spm_tools as spm
import numpy as np
from operator import itemgetter
from nilearn import image
from nipype.interfaces.dcm2nii import Dcm2nii
from nipype.interfaces import fsl
import sys

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
        data = img.get_fdata()[:,:,:]
        return img, data
    except Exception as e:
        message = "Error: " + str(e)
        if logfile:
            log_message(logfile, message, 'error')
        else:
            print(message)

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

    f = open(data,'rb')

    img_data = hdr1.raw_data_from_fileobj(f)

    analyze_img = nib.AnalyzeImage(img_data, hdr1.get_base_affine(), hdr1)

    nib.save(analyze_img,out)

def read_analyze_header(header_file,logfile):

    img = nib.load(header_file)

    zpix = img.shape[2]
    #zsize = abs(img.get_affine[2,2])
    zsize = abs(img.affine[2,2])
    xpix = img.shape[0]
    #xsize = abs(img.get_affine[0,0])
    xsize = abs(img.affine[0,0])
    ypix = img.shape[1]
    #ysize = abs(img.get_affine[1,1])
    ysize = abs(img.affine[1,1])

    return zpix, zsize, xpix, xsize, ypix, ysize

def write_interfile_header(header_file,matrix_size_x,pixel_size_x, matrix_size_y,pixel_size_y, matrix_size_z,pixel_size_z, offset_z=0):

    image_v = os.path.basename(header_file)[0:-2] + "v"
    fheader_hv = open(header_file, "w")

    offset_x = matrix_size_x/2*pixel_size_x + 0.5*pixel_size_x
    offset_y = matrix_size_y/2*pixel_size_y + 0.5*pixel_size_y

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

    # if not logfile: logfile = join(dirname(image), 'log_nii_analyze_convert.txt')

    ext = os.path.splitext(image)[1]
    img, data = nib_load(image)
    data = data.astype(np.float32) #casting to avoid problems when applying nib.save with no float data
    hdr = nib.AnalyzeHeader()
    hdr.set_data_dtype(np.float32)
    hdr.set_data_shape(data.shape)

    if ext == '.nii':
        # n2a =  rsc.get_rsc('nii2analyze', 'exe')
        if outfile:
            cimage = outfile
        else:
            cimage = image.replace('.nii', '.hdr')
        # rcommand = '%s %s %s >> %s' % (n2a, image, cimage, logfile)
        # osrun(rcommand, logfile)
        imageToWrite = nib.AnalyzeImage(data, img.affine, hdr)
    elif ext == '.hdr':
        # a2n =  rsc.get_rsc('analyze2nii', 'exe')
        if outfile:
            cimage = outfile
        else:
            cimage = image.replace('.hdr', '.nii')
        # rcommand = '%s %s %s >> %s' % (a2n, image, cimage, logfile)
        # osrun(rcommand, logfile)
        imageToWrite = nib.Nifti1Image(data, img.affine, hdr)
    else:
        # a2n =  rsc.get_rsc('analyze2nii', 'exe')
        if outfile:
            cimage = outfile
        else:
            cimage = image.replace('.img', '.nii')
        # image_hdr = str(image).replace(".img", ".hdr")
        # rcommand = '%s %s %s >> %s' % (a2n, image_hdr, cimage, logfile)
        # osrun(rcommand, logfile)
        imageToWrite = nib.Nifti1Image(data, img.affine, hdr)
    
    nib.save(imageToWrite, cimage)
    
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
        hdr = image[0:-6] + 'hdr'
        nii_analyze_convert(image,logfile=logfile, outfile=hdr)
        if exists(hdr):
            return hdr
        else:
            raise TypeError ("nifti-analyze conversion failed....")

    elif isdir(image):
        print("I think the provided image:\n %s \n is a dicom directory. I will try to convert it...")
        dicom2nii = rsc.get_rsc("dicom2nii","exe")
        nii = join(dirname(image),"image.nii")
        rcommand = '%s %s %s' % (dicom2nii, image, nii)
        osrun(rcommand,logfile)
        if exists(nii):
            hdr = nii_analyze_convert(nii,logfile=logfile)
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

        pixel_x = lines[16].split()[4]        
        pixel_size_x = lines[17].split()[5]
        pixel_y = lines[19].split()[4]
        pixel_size_y = lines[20].split()[5]
        pixel_z = lines[22].split()[4]
        pixel_size_z = lines[23].split()[5]
        
        hdr_header = image[0:-2] + "hdr" 
        # img_file = image[0:-2] + "img"
        data_file = image[0:-2] + "v"

        #This will convert .hv to .hdr and copy the data
        # gen_hdr = rsc.get_rsc("gen_hdr", "fruitcake")
        # rcommand = "%s %s %s %s %s fl %s %s %s 0" % (gen_hdr, hdr_header[0:-4], pixel_x, pixel_y, pixel_z, pixel_size_x, pixel_size_y, pixel_size_z)
        # osrun(rcommand, logfile)
        # shutil.copy(data_file, img_file)
        create_analyze_from_imgdata(data_file,hdr_header,float(pixel_x),float(pixel_y),float(pixel_z),float(pixel_size_x),float(pixel_size_y),float(pixel_size_z))
        #nii_analyze_convert("inicial.hdr",logfile,"aux.nii")
        #nii_analyze_convert("aux.nii",logfile,hdr_header)
        #os.remove("aux.nii")
        
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
    # change_format = rsc.get_rsc('change_format', 'fruitcake')
    # change_matrix = rsc.get_rsc('change_img_matrix', 'fruitcake')
    # erase_negs = rsc.get_rsc('erase_negs', 'fruitcake')
    # erase_nans = rsc.get_rsc('erase_nans', 'fruitcake')

    # Convert input image to Analyze format and float data type
    # rcommand = '%s %s %s fl >> %s' % (change_format, image_hdr, image_hdr, logfile)
    # osrun(rcommand, logfile)
    
    ## # CONTEMPLAR POSIBILIDAD DE CONVERTIR ESTO EN FUNCIÓN PARA SUSTITUIR AL "cambia_formato_hdr" de fruitcake
    change_format(image_hdr, "fl", logfile)
    
    ###
    
    # Resize image if necessary
    # ndims = recalculate_matrix(image_hdr, min_voxel_size)
    # rcommand = '%s %s %s %s %s %s novecino >> %s' % (change_matrix, image_hdr, image_hdr,
    #                                                  str(ndims[0]), str(ndims[1]), str(ndims[2]), logfile)
    # osrun(rcommand, logfile)
    image_hdr = resampleXYvoxelSizes(image_hdr, min_voxel_size, logfile)
    image_hdr = resampleZvoxelSize(image_hdr, min_voxel_size, logfile)

    # Erase negative and NaN values
    # rcommand = '%s %s %s >> %s' % (erase_negs, image_hdr, image_hdr, logfile)
    # osrun(rcommand, logfile)
    # rcommand = '%s %s %s >> %s' % (erase_nans, image_hdr, image_hdr, logfile)
    # osrun(rcommand, logfile)
    remove_neg_nan(image_hdr)
    

    return image_hdr

def recalculate_matrix(input_image, voxelsize, mode="downsampling"):

    new_dimensions = []
    image_load, data = nib_load(input_image)
    header = image_load.header
    sizes = header.get_zooms()
    dimensions = image_load.shape
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
    rois_data = rois_img.get_fdata()[:, :, :]
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
    #:param operation: 1 = multiply, 2 = divide
    :param operation: 'mult' = multiply, 'div' = divide
    :param factor: operation factor
    :param output_image: output image file
    :return:
    """

    img = nib.load(input_image)
    data = img.get_fdata()[:,:,:]
    data = np.nan_to_num(data)
    

    if operation == 'mult':
        data = data * float(factor)
    elif operation == 'div':
        data = data / float(factor)
    else:
        message = "Error! Invalid operation: " +str(operation)
        print(message)
        log_message(logfile, message, 'error')

    hdr1 = nib.AnalyzeHeader()
    hdr1.set_data_dtype(img.get_data_dtype())
    hdr1.set_data_shape(img.shape)
    #hdr1.set_zooms(abs(np.diag(img.affine)))
    #hdr1.set_zooms(abs(np.diag(img.affine))[0:3])
    #hdr1.set_zooms(abs(np.diag(img.affine))[0:4])
    hdr1.set_zooms(abs(np.diag(img.affine))[0:img.ndim])

    analyze_img = nib.AnalyzeImage(data, hdr1.get_base_affine(), hdr1)
    
    nib.save(analyze_img,output_image)


def operate_images_analyze(image1, image2, out_image, operation='mult'):
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
    hdr1.set_data_shape(img1.shape)
    ##hdr1.set_zooms(abs(np.diag(img1.affine))[0:3])
    ##hdr1.set_zooms(abs(np.diag(img1.affine))[0:4])
    hdr1.set_zooms(abs(np.diag(img1.affine))[0:img1.ndim])
    
    analyze_img = nib.AnalyzeImage(res_data, hdr1.get_base_affine(), hdr1)    

    nib.save(analyze_img,out_image)

def smooth_analyze(image,fwhm, output):

    from nibabel import processing as nibproc

    img =nib.load(image)
    smoothed=nibproc.smooth_image(img,fwhm,out_class=nib.AnalyzeImage)
    nib.save(smoothed,output)

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

def reorient_dcmtonii(image_path):
    
    
    components=os.path.split(image_path)
    path = components[0]
    image = components[1]
    converter = Dcm2nii()
    converter.inputs.source_names=[image_path]
    converter.inputs.reorient_and_crop=True
    # converter.nii_output=False
    converter.run()
    
    reor_ima_name = "o"+image
    if exists(join(path,reor_ima_name)):
        shutil.copy(join(path,reor_ima_name),image_path)
        os.remove(join(path,reor_ima_name))
        os.remove(join(path,"co"+image))
    else:
    #     converter.inputs_reorient_and_crop=False	
    #     converter.run()
    #     shutil.copy(join(path,"f"+image), image_path)
        os.remove(join(path,"c"+image))
    #     os.remove(join(path,"f"+image))

    
    
def petmr2maps(pet_image, mri_image, ct_image, log_file, spm_run, output_dir, mode="SimSET"):
        """
        It will create act and att maps from PET and MR images.
        Required inputs are:
        pet_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mri_image: dicom_dir, nii.gz, nii or Analyze (.hdr or .img)
        mode: Choose STIR or SIMSET. The maps will be different for each simulation.
        The inputs will be stored to Data/simulation_name/Patient as reformatted/corregistered Analyze
        #The maps will be stored on Data/simulation_name/Maps
        The maps will be stored on Results/output_name/Maps
        """
        message = "GENERATING ACT AND ATT MAPS FROM PET, (CT) and MR IMAGES"
        log_message(log_file, message, mode='info')
        
        reorient_dcmtonii(pet_image)
        reorient_dcmtonii(mri_image)
        reorient_dcmtonii(ct_image)
        #First of all lets take all to analyze
        pet_hdr = anything_to_hdr_convert(pet_image)
        #pet_hdr = copy_analyze(pet_hdr,image2=False,dest_dir=patient_dir)
        pet_hdr = prepare_input_image(pet_hdr,log_file,min_voxel_size=1.5)
        pet_img = pet_hdr[0:-3]+"img"
        
        if ct_image: #ct_image is not empty
            ct_hdr = anything_to_hdr_convert(ct_image)
            ct_hdr = prepare_input_image(ct_hdr,log_file,min_voxel_size=1.5)
            ct_img = ct_hdr[0:-3]+"img"

        mri_hdr = anything_to_hdr_convert(mri_image)
        #mri_hdr = copy_analyze(mri_hdr,image2=False,dest_dir=patient_dir)
        mri_hdr = prepare_input_image(mri_hdr,log_file,min_voxel_size=1.5)
        mri_img = mri_hdr[0:-3]+"img"

        #make mri image square 
        makeImageSquare(mri_hdr, log_file)

        #Performing PET-CT/MR coregister
        mfile = os.path.join(output_dir,"fusion_pet_to_mri.m")
        # correg_pet_hdr = fsl_flirt(mri_hdr, pet_hdr, log_file)
        # correg_pet_img =correg_pet_hdr[0:-3]+"img"
        correg_pet_img = spm.image_fusion(spm_run, mfile, mri_img, pet_img, log_file)
        correg_ct_img=""
        if ct_image: #ct_image is not empty
            mfile = os.path.join(output_dir,"fusion_ct_to_mri.m")
            correg_ct_img = spm.image_fusion(spm_run, mfile, mri_img, ct_img, log_file)

        #Now the map generation
        from utils.patient2maps import patient2maps

        my_map_generation = patient2maps(spm_run, output_dir, log_file,
                                         mri_img, correg_pet_img, correg_ct_img, mode=mode)
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

            #rcommand = '%s %s %s 0.096 1 >> %s' % (cambia_val, att_map, new_att_map, log_file)
            rcommand = '%s %s %s 0.096 4 >> %s' % (cambia_val, att_map, new_att_map, log_file)
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

def convert_simset_sino_to_stir(input_img, output=False):

    ## To be continued....

    simset_img = nib.load(input_img)
    simset_img_data = simset_img.get_fdata()
    shape = simset_img_data.shape

    n_slices = shape[2]
    nrings = np.sqrt(n_slices)
    n_x = shape[0]

    input_definition = []

    for i in range(n_slices):
        
        ring1,ring2 = divmod(i,nrings)
        segment = ring1 - ring2
        slice_def = [i, ring1, ring2, segment]
        input_definition.append(slice_def)

    output_definition = sorted(input_definition, key=itemgetter(3))
    stir_img_data = np.empty(shape, dtype=float, order='C')
    stir_img_data_flip_x = np.empty(shape, dtype=float, order='C')

    for i in range(n_slices):

        output_index = output_definition[i][0]
        input_slice = simset_img_data[:,:,output_index]
        stir_img_data[:,:,i] = input_slice

    for j in range(n_x):
        stir_img_data_flip_x[j,:,:] = stir_img_data[n_x-1-j, :, :]
        
    #stir_img = nib.AnalyzeImage(stir_img_data, simset_img.affine, simset_img.header)
    stir_img = nib.AnalyzeImage(stir_img_data_flip_x, simset_img.affine, simset_img.header)

    if not output:
        output = input_img [0:-4] + '_stir.hdr'
  
    nib.save(stir_img,output)
    
def resampleXYvoxelSizes(image_hdr, xyVoxelSize, log_file):

    img = nib.load(image_hdr)
    z_VoxelSize =img.header['pixdim'][3]
    target_affine = np.diag((xyVoxelSize,xyVoxelSize,z_VoxelSize))
    res_img=image.resample_img(image_hdr[0:-3]+'img',target_affine)
    nib.save(res_img,image_hdr)
    # res_img=image.resample_img(image_hdr,target_affine)
    # nib.save(res_img,image_hdr[0:-4]+"_resXY.hdr")
    
    return image_hdr


def resampleZvoxelSize(image_hdr, zOutputvoxelSize, log_file):
    img = nib.load(image_hdr)
    x_VoxelSize = img.header['pixdim'][1]
    y_VoxelSize = img.header['pixdim'][2]
    target_affine =  np.diag((x_VoxelSize,y_VoxelSize,zOutputvoxelSize))
    res_img=image.resample_img(image_hdr[0:-3]+'img',target_affine)
    nib.save(res_img,image_hdr)
    # res_img=image.resample_img(image_hdr,target_affine)
    # nib.save(res_img,image_hdr[0:-4]+"_resZ.hdr")
    
    return image_hdr


def makeImageSquare(image_hdr, log_file):
    
    # Tools for image manipulation
    corta_pega_filcol_hdr = rsc.get_rsc('corta_pega_filcol_hdr', 'fruitcake') 
    zpix, zsize, xpix, xsize, ypix, ysize = read_analyze_header(image_hdr,log_file)
    
    pixDif = abs(xpix-ypix)
    
    if pixDif != 0:
        if pixDif % 2 == 0:
            oneSide = pixDif/2
            otherSide = oneSide
        else:
            oneSide = np.trunc(pixDif/2)
            otherSide = oneSide +1
        
        if xpix > ypix:  
            rcommand1 = '%s %s %s peg %s %s >> %s' % (corta_pega_filcol_hdr, image_hdr, image_hdr, "1", str(oneSide), log_file)
            rcommand2 = '%s %s %s peg %s %s >> %s' % (corta_pega_filcol_hdr, image_hdr, image_hdr, "2", str(otherSide), log_file)
        elif ypix > xpix:
            rcommand1 = '%s %s %s peg %s %s >> %s' % (corta_pega_filcol_hdr, image_hdr, image_hdr, "3", str(oneSide), log_file)
            rcommand2 = '%s %s %s peg %s %s >> %s' % (corta_pega_filcol_hdr, image_hdr, image_hdr, "4", str(otherSide), log_file)
            
        osrun(rcommand1, log_file)
        osrun(rcommand2, log_file)


def scalImage(image_hdr, maxValue, log_file):
    """
    Given the input image_hdr (analyze format), this function scales their values to the input maxValue
    
    """
    cambia_val_interval = rsc.get_rsc('change_interval', 'fruitcake')
    img, data =nib_load(image_hdr, log_file)
    
    factor = maxValue/np.max(data)
    
    mask_hdr="mask.hdr"
    rcommand = '%s %s %s 0 0.9 0 >> %s' % (cambia_val_interval, image_hdr, mask_hdr, log_file)
    osrun(rcommand, log_file)
    rcommand = '%s %s %s 0.9 10000000000 1 >> %s' % (cambia_val_interval, mask_hdr, mask_hdr, log_file)
    osrun(rcommand, log_file)
    
    operate_single_image(image_hdr, "mult", factor, image_hdr, log_file)
    
    rcommand = '%s %s %s 0 1 1 >> %s' % (cambia_val_interval, image_hdr, image_hdr, log_file)
    osrun(rcommand, log_file)
    
    operate_images_analyze(image_hdr, mask_hdr, image_hdr, "mult") 
    
    os.remove(mask_hdr)
    os.remove("mask.img")
    
def remove_neg_nan(image_hdr):
    
    img, data = nib_load(image_hdr)
    indx = np.where(data<0)
    data[indx] = 0
    indx = np.where(np.isnan(data))
    data[indx] = 0
    
    imageToWrite = nib.AnalyzeImage(data,img.affine,img.header)
    nib.save(imageToWrite, "aux.hdr")
    copy_analyze("aux.hdr",image_hdr)
    os.remove("aux.hdr")
    os.remove("aux.img")
    
    #return image_hdr
    
def update_act_map(spmrun, act_map, att_map, orig_pet, simu_pet, output_act_map, axialFOV, log_file):
    
    output_dir = dirname(output_act_map)
    # mfileFusion = join(dirname(output_act_map),"fusion.m")
    
    # Getting the necesary resources
    # cambia_formato = rsc.get_rsc('change_format', 'fruitcake')
    # cambia_val_interval = rsc.get_rsc('change_interval', 'fruitcake') 
    # operate_image_hdr = rsc.get_rsc('operate_image', 'fruitcake')
    # remove_nan_hdr = rsc.get_rsc('erase_nans', 'fruitcake')
    # remove_neg_hdr = rsc.get_rsc('erase_negs', 'fruitcake')
        
    # First step is coregistering the output image with the orig pet (coregistered to the mri)
    #act_map_img = act_map[0:-3]+"img"
    # simu_pet_img = simu_pet[0:-3]+"img"
    orig_pet_img = orig_pet[0:-3]+"img"
    # coreg_simpet_img = spm.image_fusion(spmrun, mfileFusion, orig_pet_img, simu_pet_img, log_file)
    coreg_simpet_hdr = fsl_flirt(orig_pet, simu_pet, log_file)
    coreg_simpet_img =coreg_simpet_hdr[0:-3]+"img"
    
    act, act_data = nib_load(act_map)
    
    
    # Next, we will do a scaling by the mean
    norm_factor = proportional_scaling(coreg_simpet_hdr, orig_pet, orig_pet, log_file)
    operate_single_image(coreg_simpet_hdr,'mult',norm_factor, coreg_simpet_hdr, log_file)
    
    # Now we do a smoothing of both data to avoid multiply noise and perform the division
    mfileSmooth = join(dirname(output_act_map),"smooth.m")
    division_hdr = join(output_dir, "division.hdr")
    s_coreg_simpet_img = spm.smoothing(spmrun, mfileSmooth, coreg_simpet_img, 5, "s", log_file)    
    s_orig_pet_img = spm.smoothing(spmrun, mfileSmooth, orig_pet_img, 5, "s", log_file)
    
    s_coreg_simpet_hdr = s_coreg_simpet_img[0:-3]+"hdr"
    s_orig_pet_hdr = s_orig_pet_img[0:-3]+"hdr"
    operate_images_analyze(s_orig_pet_hdr, s_coreg_simpet_hdr, division_hdr, 'div')
    # rcommand = '%s %s %s %s fl divid' % (operate_image_hdr, s_orig_pet_hdr, s_coreg_simpet_hdr, division_hdr)
    # osrun(rcommand, log_file)
    
    # Now we do some stuff on the division image to avoid problems
    pet_mask_hdr = join(dirname(orig_pet), "pet_mask.hdr")    
    deleteValuesOutFov(pet_mask_hdr, axialFOV/2, act.shape[2]/2)
    
    # rcommand = '%s %s %s %s fl multi' % (operate_image_hdr, division_hdr, pet_mask_hdr, division_hdr)
    # osrun(rcommand, log_file)
    # rcommand = '%s %s %s >> %s' % (remove_nan_hdr, division_hdr, division_hdr, log_file)
    # osrun(rcommand, log_file)
    # rcommand = '%s %s %s >> %s' % (remove_neg_hdr, division_hdr, division_hdr, log_file)
    # osrun(rcommand, log_file)
    fix_4d_image(pet_mask_hdr)
    operate_images_analyze(division_hdr, pet_mask_hdr, division_hdr, "mult")
    remove_neg_nan(division_hdr)
    change_interval_values(division_hdr, division_hdr, 5, 100000000000000000000000000000000000,1)
    # rcommand = '%s %s %s 5 100000000000000000000000000000000000 1' % (cambia_val_interval, division_hdr, division_hdr)
    # osrun(rcommand, log_file)
    
    #operate_images_analyze(division_hdr, pet_mask_hdr, division_hdr, 'mult')
    operate_images_analyze(division_hdr, pet_mask_hdr, division_hdr, "mult")
    # rcommand = '%s %s %s %s fl multi' % (operate_image_hdr, division_hdr, pet_mask_hdr, division_hdr)
    # osrun(rcommand, log_file)
    
    #and finally, we calculate the new activity image 
    fix_4d_image(act_map)
    operate_images_analyze(division_hdr, act_map, output_act_map, "mult")
    # rcommand = '%s %s %s %s fl multi' % (operate_image_hdr, act_map, division_hdr, output_act_map)
    # osrun(rcommand, log_file)    
    scalImage(output_act_map, 127, log_file) 
    change_format(output_act_map,"1B", log_file)
    # rcommand = '%s %s %s 1B >> %s' % (cambia_formato, output_act_map, output_act_map, log_file)
    # osrun(rcommand, log_file)  
    
def fsl_flirt(reference_hdr, input_hdr, log_file):
    components = os.path.split(input_hdr)
    coreg_hdr = os.path.join(components[0], 'r' + components[1])
    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.in_file = input_hdr
    flt.inputs.reference = reference_hdr
    flt.out_file = coreg_hdr
    flt.out_log=log_file
    flt.save_log=True
    flt.inputs.output_type = "NIFTI_GZ"
    flt.cmdline 
    'flirt -in %s -ref %s -out %s -dof 6 -cost mutualinfo -searchrx -30 30 -searchry -30 30 -searchrz -30 30' %(input_hdr, reference_hdr, coreg_hdr)
    aux = os.getcwd()
    os.chdir(components[0])
    flt.run()
    os.chdir(aux)
    
    anything_to_hdr_convert(input_hdr[0:-4]+"_flirt.nii.gz")
    copy_analyze(input_hdr[0:-4]+"_flirt.hdr", coreg_hdr)
    os.system("rm %s*" % input_hdr[0:-4]+"_flirt.*")
    
    return coreg_hdr
    
      
def proportional_scaling(img,ref_img,mask_img, log_file):

    img_max, img_mean = compute_vmax_vmean(img, mask_img)
    ref_max, ref_mean = compute_vmax_vmean(ref_img, mask_img)

    if float(img_mean) != 0:
        fnorm = ref_mean / img_mean
        return fnorm
    else:        
        message = 'Error scaling image. Image maean value is zero: ' + str(img)
        log_message(log_file, message, 'error')
        #print message  

def compute_vmax_vmean(img, mask_img):
    """
    Compute maximum and mean intensity values on input image counting 
    on voxels inside the reference image (brain mask)
    :param img: (string) input image path
    :param ref_img: (string) reference image path
    :return: 
    """

    img, data = nib_load(img)
    data = np.nan_to_num(data) 

    ref_img, data_ref = nib_load(mask_img)
    data_ref = np.nan_to_num(data_ref)

    i_max = np.amax(data_ref)

    super_threshold_indices = data_ref > 0.2*i_max
    data_ref[super_threshold_indices] = 0

    # Compute values restricted to voxels inside mask (ref image)
    indx = np.where((data>0) & (data_ref.reshape(data.shape)>0))

    # Maximum intensity value
    v_max = np.max(data[indx])
    # Mean intensity value
    v_mean = np.mean(data[indx])

    return v_max, v_mean 


def deleteValuesOutFov(mask_hdr, max_z, central_slice):
    
    img, data = nib_load(mask_hdr)
    data = np.nan_to_num(data)
    
    z = img.shape[2]
    z_size = img.header['pixdim'][3] #mm
    max_z = int(round((float(max_z)*10)/float(z_size))) 
    
    i_min = int(central_slice)-max_z
    i_max = int(central_slice)+max_z 
    
    for i in range(0, i_min):
        data[:,:,i]=0
    
    for i in range(i_max,z):
        data[:,:,i]=0

    img_to_write = nib.Nifti1Image(data, img.affine, img.header)
    nib.save(img_to_write,mask_hdr)
    
def compute_corr_coeff(img1, img2, log_file):
    """
    Compute the correlation coefficiente between img1 and img2 
    :param img1: (string) input header image1 path
    :param img2: (string) input header image2 path
    :return: 
    """
    
    img1_img, img1_data = nib_load(img1, log_file)
    img2_img, img2_data = nib_load(img2, log_file)
    corrCoefmtx = np.corrcoef(img1_data.flatten(),img2_data.flatten())
    
    return corrCoefmtx[0,1]

def fix_4d_image(image_hdr):
    img, data = nib_load(image_hdr)
    shape = data.shape
   
    if len(shape) != 3:
        data_new = data[:,:,:,0]
        
        imageToWrite = nib.AnalyzeImage(data_new,img.affine,img.header)
        nib.save(imageToWrite, "aux.hdr")
        copy_analyze("aux.hdr",image_hdr)
        os.remove("aux.hdr")
        os.remove("aux.img")
    
def change_interval_values(input_hdr, output_hdr, min_value, max_value, rep_value):
    img, data = nib_load(input_hdr)
    
    
    indx = np.where(data<max_value) and np.where(data>min_value)
    
    data[indx] = rep_value    
    
    imageToWrite = nib.AnalyzeImage(data,img.affine,img.header)
    nib.save(imageToWrite, "aux.hdr")
    copy_analyze("aux.hdr",output_hdr)
    os.remove("aux.hdr")
    os.remove("aux.img")

def change_format(image_hdr, newFormat, logfile):
    message=""
    img, data = nib_load(image_hdr)
    
    if newFormat == "fl":
        form=np.float32
    elif newFormat == "1B":
        form=np.uint8
    else:
        message = "Error! Invalid format (or not implemented yet): " +str(newFormat)
        print(message)
        log_message(logfile, message, 'error')
        if message=="":
        data = data.astype(form) 
        hdr = nib.AnalyzeHeader()
        hdr.set_data_dtype(form)
        hdr.set_data_shape(data.shape)
        imageToWrite = nib.AnalyzeImage(data, img.affine, hdr)    
        nib.save(imageToWrite, image_hdr)
    
    return image_hdr

def fix_4d_data(data):
    
    shape = data.shape

    if len(shape) == 3:
        return data
    else:
        return data[:,:,:,0]

def remove_neg_nan(data):
    
    indx = np.where(data<0)
    data[indx] = 0
    indx = np.where(np.isnan(data))
    data[indx] = 0
