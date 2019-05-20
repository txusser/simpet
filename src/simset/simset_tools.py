import random
import os
from os.path import join

def make_simset_act_table (act_table_factor,my_act_table):

    with open(my_act_table, 'w') as f:
        f.write("256\n")
        for i in range(256):
            act_value = i*0.000001*act_table_factor
            f.write(str('{:.12f}'.format(act_value))+"\n")
    f.close()

def make_simset_phg(config, output_file, simulation_dir, act,
                    scanner_radius, center_slice,
                    photons, sim_time, 
                    add_randoms=False, phg_hf=False, S=0):

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
        print("Importance sampling techniques are being deactivated since add_randoms is on")
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
    xMin, xMax = -act_fov[0,0]/20, act_fov[0,0]/20 # 20 is because it must be cm
    yMin, yMax = -act_fov[1,1]/20, act_fov[1,1]/20

    z_offset = abs(act.affine[2,2]*center_slice/10) #cm
    zMin, zMax = -z_offset, act_fov[2,2]/10 - z_offset

    dz = (zMax-zMin)/nslices

    # Directory variables
    simset_dir = config.get("dir_simset")
    simset_phgdata_dir = join(simset_dir,"phg_data")

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
            f.write(
                "\n		NUM_ELEMENTS_IN_LIST	slice = 9 " +
                "\n		INT	slice_number  = %s" % str(i) +
                "\n		REAL	zMin = %s" % str(zMin + i*dz) +
                "\n		REAL	zMax = %s" % str(zMin + (i+1)*dz) +
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
        f.write("\n	REAL	target_zMin = %s" % str(zMin))
        f.write("\n	REAL	target_zMax = %s" % str(zMax))
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

    f.close

def make_simset_bin(config, output_file, scanner):

    stir_identifier = "# Hello, I am a SimSET BIN file!\n"

    # define types to be used
    boolean = "BOOL		"
    real    = "REAL		"
    integer = "INT	    "
    string  = "STR      "

    # Here we get the parameters from the parameter files.
    scatter_param = str(config.get("scatter_param"))
    min_s = str(config.get("min_s"))
    max_s = str(config.get("max_s"))
    num_z_bins = str(scanner.get("num_rings"))
    axial_fov = scanner.get("axial_fov")
    min_z, max_z = -axial_fov/2, axial_fov/2
    num_aa_bins = str(scanner.get("num_aa_bins"))
    num_td_bins = str(scanner.get("num_td_bins"))
    min_td = str(scanner.get("min_td"))
    max_td = str(scanner.get("max_td"))

    with open (output_file, 'w') as f:
        f.write(stir_identifier)
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
        

def make_simset_cyl_det(scanner_params, output, sim_dir, det_hf=0):
        
    num_rings = scanner_params.get("num_rings")
    z_crystal_size = scanner_params.get("z_crystal_size")
    max_z = scanner_params.get("max_z")
    min_z = scanner_params.get("min_z")
    gap_z_size = (max_z-min_z-z_crystal_size*num_rings)/(num_rings-1)
    cyln_inner_radius = scanner_params.get("scanner_radius")
    cyln_outer_radius = cyln_inner_radius + scanner_params.get("crystal_thickness")
    energy_resolution = scanner_params.get("energy_resolution")
    timing_resolution = scanner_params.get("timing_resolution")
    material = scanner_params.get("simset_material")

    nrings_total = 2*num_rings-1

    print "Number of rings in the scanner is: %s" % num_rings
    print "Cristal z is: %s cm" % z_crystal_size
    print "Gaps are: %s cm" % gap_z_size
    print "Ring thickness is: %s cm" % (cyln_outer_radius-cyln_inner_radius)
    print "Energy resolution is: %s" % energy_resolution
    print "Timing resolution is: %s" % timing_resolution

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
    