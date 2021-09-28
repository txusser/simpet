import os, sys
from os.path import join,exists


simpet_path = "/home/jsilva/Work/repositories/simpet"
sys.path.insert(0,simpet_path)

from simpet import wholebody_simulation

config_yml = join(simpet_path,'config.yml')
params_yml = join(simpet_path,'initialParams.yml')

act_name = "ACT_map_5.hdr" # Note that for this to work the ACT and ATT should be named the same for all patients
att_name = "ATT_map_5.hdr"

maps_dir = join(simpet_path,'Data')
maps_list = sorted(os.listdir(maps_dir))

# Iterates over the directory to process all patients
for patient in maps_list:

    patient_dir = join(maps_dir,str(patient))
    patient_params = join(patient_dir, 'params.yml')

    # Creates a new params file that goes inside the patient folder.
    f_old = open(params_yml,'r')
    f_new = open(patient_params,'w')

    lines = f_old.readlines()
    for line in lines:
        if line.startswith('patient_dirname'):
            line = ('patient_dirname: "%s"\n' % patient)
        if line.startswith('act_map'):
            line = ('act_map: "%s"\n' % act_name)
        if line.startswith('att_map'):
            line = ('att_map: "%s"\n' % att_name)
        if line.startswith('output_dir'):
            line = ('output_dir: "%s"\n' % patient)
        
        f_new.write(line)
    f_old.close()
    f_new.close()

    #Checks if a patient's output already exists
    output_file_to_test = join(simpet_path,'Results',patient,'rec_OSEM3D_32.hdr')
    if exists(output_file_to_test):
        print('Skipping patient %s. Reconstructed WB image already exists' % patient)
    else:
        print("Now I will run Simpet WB simulation for patient %s" % patient)
        patient_simpet = wholebody_simulation(param_file=patient_params,config_file=config_yml)
        patient_simpet.run()

