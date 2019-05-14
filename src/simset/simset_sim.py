from os.path import join,dirname,abspath,isdir
import os
import shutil
import datetime
from utils import resources as rsc
from utils import tools
import yaml

class SimSET_Simulation(object):
    """
    This class provides main SimPET functions.
    You have to initialize the class with a simulation_name.

    A directory structure will be created under Data/simulation_name including:
    Data/simulation_name/Patient: If your process starts with PET and MR images, they will be copied here
    Data/simulation_name/Maps: If your process starts with act and att maps, they will be copied here
    Data/simulation_name/Results: Your sim results and brainviset results will be stored here

    This class is meant to work out of the box.
    You need Matlab MCR v901 in order to run this. It is possible that you need to modify the self.matlab_mcr_path.
    MCR Paths working out of the box are:
    /opt/MATLAB/MATLAB_Compiler_Runtime/v901/
    /usr/local/MATLAB/MATLAB_Runtime/v901/
    """

    def __init__(self,param_file,act_map,att_map):

        #Initialization
        self.simpet_dir = dirname(abspath(__file__))
        self.dir_data = join(self.simpet_dir, "Data")

        with open(param_file, 'rb') as f:
            params = yaml.load(f.read(), Loader=yaml.FullLoader)

        scanner = params.get("scanner")



    def run(self):
        print "Working on it"
        