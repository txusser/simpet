import random
import os, shutil, time, sys
import subprocess as sp
from os.path import join, exists
import nibabel as nib
import numpy as np
import pexpect
import yaml

from utils import tools

def make_simset_act_table (act_table_factor, my_act_table, log_file=False):

    with open(my_act_table, 'w') as f:
        f.write("256\n")
        for i in range(256):
            act_value = i*0.000001*act_table_factor
            f.write(str('{:.12f}'.format(act_value))+"\n")
    f.close()

    if log_file:
        message = "Wrote act_table with factor %s" % act_table_factor
        tools.log_message(log_file,message,'info')

def make_simset_phg(config, output_file, simulation_dir, act,
                    scanner_radius, scanner_axial_fov, center_slice,
                    photons, sim_time,
                    add_randoms=False, phg_hf=False, S=0, log_file=False):

    stir_identifier = "# Hello, I am a SimSET PHG file!\n"

    # define types to be used
    boolean = "BOOL		"
    real    = "REAL		"
    longl   = "LONGLONG "
    integer = "INT	    "
    enum    = "ENUM 	"
    string  = "STR      "

    #Configuring the importance sampling parameters
    if add_randoms==1:
        stratification = "false"
        forced_detection = "false"
        non_absortion = "false"
        # We need to force coincidences + singles for randoms
        sim_PET_coinc_only = "false"
        sim_PET_coinc_plus_singles = "true"
    else:
        stratification = config.get("stratification")
        forced_detection = config.get("forced_detection")
        non_absortion = config.get("forced_non_absortion")
        sim_PET_coinc_only = "true"
        sim_PET_coinc_plus_singles = "false"

    # Configuration of photons an simulation time

    num_to_simulate = str(photons)
    length_of_scan = str(sim_time)

    # Import other configurations form config.yml
    acceptance_angle = str(config.get("acceptance_angle"))
    positron_range = config.get("positron_range")
    non_col = config.get("non_colinearity")
    minimum_energy = str(config.get("minimum_energy"))
    weight_window_ratio = str(config.get("weight_window_ratio"))
    point_source_voxels = config.get("point_source_voxels")
    coherent_scatter_object = config.get("coherent_scatter_object")
    coherent_scatter_detector = config.get("coherent_scatter_detector")
    simulated_isotope = config.get("isotope")

    # Generate a random seed for the MC
    random_seed = str(random.randint(1,1e12))

    # Object stuff
    nslices = act.shape[2]
    xbins = act.shape[0]
    ybins = act.shape[1]

    act_fov = abs(act.shape*act.affine)
    xMin, xMax = round(-act_fov[0,0]/20,3), round(act_fov[0,0]/20,3) # 20 is because it must be cm
    yMin, yMax = round(-act_fov[1,1]/20,3), round(act_fov[1,1]/20,3)

    z_offset = abs(act.affine[2,2]*center_slice/10 + 0.5*act.affine[2,2]/10) #cm
    zMin, zMax = round(-z_offset,2), round(act_fov[2,2]/10 - z_offset,2)

    dz = round((zMax-zMin)/nslices,2)

    max_z_target = scanner_axial_fov/2
    min_z_target = -scanner_axial_fov/2

    # Directory variables
    simset_dir = config.get("dir_simset")
    simset_phgdata_dir = join(simset_dir,"phg.data")

    # Now we write the phg file
    with open (output_file, 'w') as f:

        # First we write the configuration stuff for the simulation
        f.write(stir_identifier)
        f.write("\n\n# Runtime options\n")
        f.write(boolean + "simulate_stratification = %s \n" % stratification)
        f.write(boolean + "simulate_forced_detection = " + forced_detection + "\n")
        f.write(boolean + "forced_non_absorbtion = " + non_absortion + "\n")
        f.write(real + "acceptance_angle = " +  acceptance_angle + "\n")
        f.write(longl + "num_to_simulate = " + num_to_simulate + "\n")
        f.write(real + "length_of_scan = " + length_of_scan + "\n")
        f.write(boolean + "simulate_SPECT = false\n")
        f.write(boolean + "simulate_PET_coincidences_only = " + sim_PET_coinc_only + "\n")
        f.write(boolean + "simulate_PET_coincidences_plus_singles = " + sim_PET_coinc_plus_singles + "\n")
        f.write(boolean + "adjust_for_positron_range = " + positron_range + "\n")
        f.write(boolean + "adjust_for_collinearity = " + non_col + "\n")
        f.write(real + "minimum_energy = " + minimum_energy + "\n")
        f.write(real + "photon_energy = 511.0\n")
        f.write(real + "weight_window_ratio = " + weight_window_ratio + "\n")
        f.write(boolean + "point_source_voxels = " + point_source_voxels + "\n")
        f.write(integer + "random_seed = " + random_seed + "\n")
        f.write(boolean + "model_coherent_scatter_in_obj = " + coherent_scatter_object + "\n")
        f.write(boolean + "model_coherent_scatter_in_tomo = " + coherent_scatter_detector + "\n")
        f.write(enum + "isotope = " + simulated_isotope + "\n")

        # Now comes the object stuff (old make_phg_simset from fruitcake)
        f.write("\n\n# OBJECT GEOMETRY VALUES\n")
        f.write("\nNUM_ELEMENTS_IN_LIST   object = %s" % str(nslices+1))
        f.write("\n		INT		num_slices = %s" % str(nslices))
        
        for i in range(nslices):
            zMin_value=round(zMin + i*dz,2)
            zMax_value=round(zMin +(i+1)*dz,2)
            f.write(
                "\n		NUM_ELEMENTS_IN_LIST	slice = 9 " +
                "\n		INT	slice_number  = %s" % str(i) +
                "\n		REAL	zMin = %s" % str(zMin_value) +
                "\n		REAL	zMax = %s" % str(zMax_value) +
                "\n		REAL	xMin = %s" % str(xMin) +
                "\n		REAL	xMax = %s" % str(xMax) +
                "\n		REAL	yMin = %s" % str(yMin) +
                "\n		REAL	yMax = %s" % str(yMax) +
                "\n		INT	num_X_bins = %s" % str(xbins) +
                "\n		INT	num_Y_bins = %s" % str(ybins)
                )

        # Now we fill the values for the target cylinder

        f.write("\n\n# TARGET CYLINDER INFORMATION")
        f.write("\nNUM_ELEMENTS_IN_LIST    target_cylinder = 3")
        f.write("\n	REAL	target_zMin = %s" % str(min_z_target))
        f.write("\n	REAL	target_zMax = %s" % str(max_z_target))
        f.write("\n	REAL	radius =      %s\n\n" % str(scanner_radius))


        # Now we need the directory stuff
        f.write(string + 'coherent_scatter_table = "' + join(simset_phgdata_dir,"coh.tables") + '"\n')
        f.write(string + 'activity_indexes = "' + join(simulation_dir,"rec.act_indexes") + '"\n')
        f.write(string + 'activity_table = "' + join(simulation_dir,"phg_act_table") + '"\n')
        f.write(string + 'activity_index_trans = "' + join(simset_phgdata_dir,"phg_act_index_trans") + '"\n')
        f.write(string + 'activity_image = "' + join(simulation_dir,"rec.activity_image") + '"\n')
        f.write(string + 'attenuation_indexes = "' + join(simulation_dir,"rec.att_indexes") + '"\n')
        f.write(string + 'attenuation_table = "' + join(simset_phgdata_dir,"phg_att_table") + '"\n')
        f.write(string + 'attenuation_index_trans = "' + join(simset_phgdata_dir,"phg_att_index_trans") + '"\n')
        f.write(string + 'attenuation_image = "' + join(simulation_dir,"rec.attenuation_image") + '"\n')

        # This part changes productivity tables between S=0 and S=1 adq
        if S==1:
            f.write(string + 'productivity_input_table = "' + join(simulation_dir,"sampling_rec") + '"\n')
            f.write(string + 'productivity_output_table = ""\n')
        else:
            f.write(string + 'productivity_input_table = ""\n')
            f.write(string + 'productivity_output_table = "' + join(simulation_dir,"sampling_rec") + '"\n')

        f.write(string + 'statistics_file = "' + join(simulation_dir,"rec.stat") + '"\n')
        f.write(string + 'isotope_data_file = "' + join(simset_phgdata_dir,"isotope_positron_energy_data") + '"\n')
        f.write(string + 'detector_params_file = "' + join(simulation_dir,"det.rec") + '"\n')
        f.write(string + 'bin_params_file = "' + join(simulation_dir,"bin.rec") + '"\n')
        # Adds the phg history file if it is activated
        if phg_hf==1:
            f.write(string + 'history_file = "' + join(simulation_dir, "phg_hf.hist" + '"\n'))

    f.close()

    if log_file:
        message = "Created phg_file in: %s" % output_file
        tools.log_message(log_file,message,'info')

def make_simset_bin(config, output_file, simulation_dir, scanner, add_randoms=False, log_file=False):

    stir_identifier = "# Hello, I am a SimSET BIN file!\n"

    # define types to be used
    boolean = "BOOL		"
    real    = "REAL		"
    integer = "INT	    "
    string  = "STR      "

    # We will create an extra bin for randoms if the randoms simulation is activated.
    if add_randoms:
        accept_randoms = "true"
        scatter_param = "6"
    else:
        accept_randoms = "false"
        scatter_param = "1"

    min_s = "0"
    max_s = "9"

    # Here we get the parameters from the parameter files.
    num_z_bins = str(scanner.get("num_rings"))
    axial_fov = scanner.get("axial_fov")
    min_z, max_z = -axial_fov/2, axial_fov/2
    num_aa_bins = str(scanner.get("num_aa_bins"))
    num_td_bins = str(scanner.get("num_td_bins"))
    min_td = str(-scanner.get("scanner_radius"))
    max_td = str(scanner.get("scanner_radius"))
    min_e = str(scanner.get("min_energy_window"))
    max_e = str(scanner.get("max_energy_window"))
    rec_weight_file = join(simulation_dir,"rec.weight")

    with open (output_file, 'w') as f:
        f.write(stir_identifier)
        f.write(boolean + " accept_randoms = " + accept_randoms + "\n")
        f.write(integer + "scatter_param = " + scatter_param + "\n")
        f.write(integer + "min_s = " + min_s + "\n")
        f.write(integer + "max_s = " + max_s + "\n")
        f.write(integer + "num_z_bins = " + num_z_bins + "\n")
        f.write(real + "min_z = " + str(min_z) + "\n")
        f.write(real + "max_z = " + str(max_z) + "\n")
        f.write(integer + "num_aa_bins = " + num_aa_bins + "\n")
        f.write(integer + "num_td_bins = " + num_td_bins + "\n")
        f.write(real + "min_td = " + min_td + "\n")
        f.write(real + "max_td = " + max_td + "\n")
        f.write("INT     num_e1_bins = 1\n")
        f.write("INT     num_e2_bins = 1\n")
        f.write(real + "min_e = " + min_e + "\n")
        f.write(real + "max_e = " + max_e + "\n")
        f.write("INT     weight_image_type = 2\n")
        f.write("INT     count_image_type	= 2\n")
        f.write("BOOL	 add_to_existing_img = false\n")
        f.write(string + 'weight_image_path = "' + rec_weight_file + '"\n')

    f.close()

    if log_file:
        message = "Created bin_file in: %s" % output_file
        tools.log_message(log_file,message,'info')

def make_simset_cyl_det(scanner_params, output, sim_dir, det_hf=0, log_file=False):

    num_rings = scanner_params.get("num_rings")
    z_crystal_size = scanner_params.get("z_crystal_size")
    axial_fov = scanner_params.get("axial_fov")
    max_z = axial_fov/2
    min_z = -axial_fov/2
    gap_z_size = (max_z-min_z-z_crystal_size*num_rings)/(num_rings-1)
    cyln_inner_radius = scanner_params.get("scanner_radius")
    cyln_outer_radius = cyln_inner_radius + scanner_params.get("crystal_thickness")
    energy_resolution = scanner_params.get("energy_resolution")
    timing_resolution = scanner_params.get("timing_resolution")
    material = scanner_params.get("simset_material")

    nrings_total = 2*num_rings-1

    new_file = open(output, "w")
    new_file.write(
        "ENUM detector_type = cylindrical \n\n" +
        "# This detector example has %s axial rings and %s gaps \n" % (num_rings,num_rings-1) +
        "INT	cyln_num_rings = %s \n\n" % nrings_total
        )

    for i in range(1,num_rings+1):

        ring_zmin = min_z + (i-1)*z_crystal_size + (i-1)*gap_z_size
        ring_zmax = ring_zmin + z_crystal_size
        gap_zmax = ring_zmin + z_crystal_size + gap_z_size

        new_file.write(
            "# RING #%s \n" % i +
            "# The following defines the ring parameters \n" +
            "LIST	cyln_ring_info_list = 5 \n" +
            "INT	cyln_num_layers = 1 \n" +
	        "LIST	cyln_layer_info_list = 4 \n" +
	        "BOOL	cyln_layer_is_active = TRUE \n" +
	    	"INT	cyln_layer_material = %s \n" % material +
	    	"REAL	cyln_layer_inner_radius = %s \n" % cyln_inner_radius +
	    	"REAL	cyln_layer_outer_radius = %s \n" % cyln_outer_radius +
	        "REAL	cyln_min_z = %s \n" % ring_zmin +
	        "REAL	cyln_max_z = %s \n\n" % ring_zmax
        )

        if not i==num_rings:

            new_file.write(
                "# GAP #%s \n" % i +
                "# The following defines the gap parameters \n" +
                "LIST	cyln_ring_info_list = 5 \n" +
                "INT	cyln_num_layers = 1 \n" +
	            "LIST	cyln_layer_info_list = 4 \n" +
	            "BOOL	cyln_layer_is_active = FALSE \n" +
		        "INT	cyln_layer_material = 0 \n" +
		        "REAL	cyln_layer_inner_radius = %s \n" % cyln_inner_radius +
		        "REAL	cyln_layer_outer_radius = %s \n" % cyln_outer_radius +
	            "REAL	cyln_min_z = %s \n" % ring_zmax +
	            "REAL	cyln_max_z = %s \n\n" % gap_zmax
                )

    new_file.write(
        "REAL    reference_energy_keV = 511.0 \n" +
        "REAL    energy_resolution_percentage = %s \n" % energy_resolution +
        "REAL 	photon_time_fwhm_ns = %s \n" % timing_resolution
        )
    if det_hf==1:
            new_file.write('STR     history_file = "' + join(sim_dir, "det_hf.hist" + '"\n'))

    new_file.close()

    if log_file:

        message = ("Created det_file with:\n" +
                  "Cristal z: %s cm\n" % z_crystal_size +
                  "Gap size: %s cm\n" % gap_z_size +
                  "Ring thickness: %s cm" % (cyln_outer_radius-cyln_inner_radius) +
                  "Energy resolution: %s" % energy_resolution +
                  "Timing resolution: %s" % timing_resolution)

        tools.log_message(log_file,message,'info')

def make_simset_simplepet_det(scanner_params, output):
    
    energy_resolution = scanner_params.get("energy_resolution")

    new_file = open(output, "w")
    
    new_file.write(
        "ENUM detector_type = simple_pet \n\n" +
        "REAL    reference_energy_keV = 511.0 \n" +
        "REAL    energy_resolution_percentage = %s \n" % energy_resolution
        )

    new_file.close()

def make_index_file(simulation_dir, simset_dir, log_file=False):

    output = join(simulation_dir,"index_file.log")
    phg_file = join(simulation_dir, "phg.rec")
    act_dat = join(simulation_dir, "act.dat")
    att_dat = join(simulation_dir, "att.dat")
    make_index_file = join(simset_dir,"bin", "makeindexfile")

    prompts = (phg_file + "\n" + "y\n" + "y\n" + "0\n" + "y\n" + act_dat + "\n" +
               "0\n" + "0\n" + "1\n" + "n\n" + "n\n" + "y\n" + "y\n" + "0\n" + "y\n" +
               att_dat +"\n" + "0\n" + "0\n" + "1\n" + "n\n" + "n\n")

    os.system('printf "%s" | %s > %s' % (prompts, make_index_file, output))

    if log_file:
        message = 'printf "%s" | %s > %s' % (prompts, make_index_file, output)
        tools.log_message(log_file,message,'info')

def process_weights(weights_file, output_dir, scanner, add_randoms = 0):

    nbins = scanner.get("num_td_bins")
    nangles = scanner.get("num_aa_bins")
    nrings = scanner.get("num_rings")
    nslices = nrings*nrings

    Simset_offset = 32768
    block_size = nbins*nangles*nslices*4

    trues_start = Simset_offset
    trues_end = Simset_offset + block_size
    trues_file = join(output_dir,"w1")


    with open(weights_file, 'rb') as in_file:
        with open(trues_file, 'wb') as out_file:
            out_file.write(in_file.read()[trues_start:trues_end])

    output = join(output_dir,"trues.hdr")
    tools.create_analyze_from_imgdata(trues_file,output,nbins,nangles,nslices,1,1,1,"fl")
    os.remove(trues_file)

    scatter_start = trues_end
    scatter_end = trues_end + block_size
    scatter_file = join(output_dir,"w2")


    with open(weights_file, 'rb') as in_file:
        with open(scatter_file, 'wb') as out_file:
            out_file.write(in_file.read()[scatter_start:scatter_end])

    output = join(output_dir,"scatter.hdr")
    tools.create_analyze_from_imgdata(scatter_file,output,nbins,nangles,nslices,1,1,1,"fl")
    os.remove(scatter_file)

    if add_randoms == 1:

        randoms_start = scatter_end
        randoms_end = scatter_end + block_size
        randoms_file = join(output_dir,"w3")

        with open(weights_file, 'rb') as in_file:
            with open(randoms_file, 'wb') as out_file:
                out_file.write(in_file.read()[randoms_start:randoms_end])

        output = join(output_dir,"randoms.hdr")
        tools.create_analyze_from_imgdata(randoms_file,output,nbins,nangles,nslices,1,1,1,"fl")
        os.remove(randoms_file)

def add_randoms(sim_dir, simset_dir, coincidence_window, rebin=True, log_file=False):

    string  = "STR      "
    integer = "INT      "
    enum    = "ENUM 	"
    real    = "REAL		"

    sorted_file = join(sim_dir, "sorted_det_hf.hist")
    template = join(sim_dir, "sort.params")
    det_hf = join(sim_dir, "det_hf.hist")

    with open (template, 'w') as f:

        f.write(string + 'history_file = "' + det_hf + '"\n')
        f.write(string + 'sorted_history_file = "' + sorted_file + '"\n')
        f.write(integer + 'buffer_size = 1024\n')

    f.close()

    sorting_bin = join(simset_dir, "bin", "timesort -d")

    command = command = "%s %s >> %s" % (sorting_bin, template, log_file)
    tools.osrun(command, log_file)

    randoms_file = join(sim_dir, "randoms.hist")
    template = join(sim_dir, "randoms.params")

    with open (template, 'w') as f:

        f.write(enum + 'detector_type = cylindrical\n')
        f.write(string + 'history_file = "' + sorted_file + '"\n')
        f.write(string + 'randoms_history_file = "' + randoms_file + '"\n')
        f.write(real + "coincidence_timing_window_in_ns = " + str(coincidence_window) + "\n")

    f.close()

    addrand_bin = join(simset_dir, "bin", "addrandoms")

    command = "%s %s >> %s" % (addrand_bin, template, log_file)
    tools.osrun(command, log_file)
    
    if exists(sorted_file):
        os.remove(sorted_file)

    # The following will replace the existing det-hist file with the new including randoms

    if rebin:

        det_file = join(sim_dir, "det.rec")

        with open (det_file, 'r') as f:
            lines = f.readlines()
        with open(det_file, 'w') as f:
            for line in lines:
                line = line.replace("det_hf.hist", "randoms.hist")
                f.write(line)

        binfile = join(sim_dir, "phg.rec")
        phgbin = join(simset_dir, "bin", "bin -d")

        command = command = "%s %s >> %s" % (phgbin, binfile, log_file)
        tools.osrun(command, log_file)

def combine_history_files(simset_dir, history_files, output, log_file):

    combinehist = join(simset_dir, "bin", "combinehist")

    rcommand = '%s %s %s' % (combinehist, history_files, output)

    proc  = sp.Popen(rcommand, universal_newlines=True, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE).communicate("Yes\n")

    #tools.osrun(rcommand, log_file)

def simset_calcattenuation(simset_dir,sim_dir,output,hdr_to_copy,nrays=1,timeout=36000):

    calcattenuation = join(simset_dir, "bin", "calcattenuation")

    current_dir = os.getcwd()
    os.chdir(sim_dir)

    child = pexpect.spawn(calcattenuation,timeout=timeout)
    child.logfile = sys.stdout.buffer
    child.expect('Enter name of param file: ')
    child.sendline('phg.rec')
    child.expect('Enter name of output file: ')
    child.sendline(output)
    child.expect('Enter the number of sub-samples*')
    child.sendline(str(nrays))
    child.wait()

    CHUNK_SIZE = os.path.getsize(hdr_to_copy[0:-3] + 'img')
    print(CHUNK_SIZE)
    with open(output, 'rb') as f:
        chunk = f.read(CHUNK_SIZE)
    with open(output + '.img', 'wb') as chunk_file:
        chunk_file.write(chunk)
        chunk_file.close()

    shutil.copy(hdr_to_copy, output + '.hdr')

    os.chdir(current_dir)
    
