# simpet
# Developed by Jesús Silva-Rodríguez 2019
# Health Research Institute of Santiago de Compostela

The SIMPET project is intended to allow to setup and launch MC simulation on a simple way. It provides functionalities to: 

- Extract simple activity and attenuation maps from PET/MR images.
- Apply the BrainViset procedure to obtain realistic Activity and Attenuation maps.
- Run Analytic simulations using STIR simulation procedure and MC simulation using SimSET.

Just start importing the SIMPET class. 

This class provides main SimPET functions. You have to initialize the class with a simulation_name.A directory structure will be created under Data/simulation_name including:

- Data/simulation_name/Patient: If your process starts with PET and MR images, they will be copied here, reformatted and co-registered
- Data/simulation_name/Maps: If your process starts with act and att maps, they will be copied here
- Data/simulation_name/Results: Your sim results and brainviset results will be stored here
    
This class is meant to work out of the box. It is possible that you need to modify the self.matlab_mcr_path.

How to start:

Type "python" into a terminal. We recommend to install ipython interpeter, which is very handy:

from simpet import SIMPET

my_run = SIMPET("Patient1")

activity_map, attenuation_map = myrun.create_sim_maps_from_petmr("pathto/pet_patient1.nii","pathto/mri_patient2.nii",mode="STIR")




