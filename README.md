# simpet
Developed by Jesús Silva-Rodríguez 2019


The SIMPET project is intended to allow to setup and launch MC simulation on a simple way. It provides functionalities to: 

- Extract simple activity and attenuation maps from PET/MR images.
- Apply the BrainViset procedure to obtain realistic Activity and Attenuation maps.
- Run Analytic simulations using STIR simulation procedure and MC simulation using SimSET.

WARNING. The current version of the project is able to produce only sinograms and LM data using SimSET. Rest of the stuff is coming soon.

SETUP: 

- Clone the repository
- Run setup.py
- Open Python and import the simpet class.
- Create a simulation object. Sample Data is provided in Data/test: test_simu = simpet.SimPET('Data/test_image/testParams.yml')
- Run the simulation: test_simu.run()



