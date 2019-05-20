import os

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
