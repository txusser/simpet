# simpet
Developed by Jesús Silva-Rodríguez 2019


The SIMPET project is intended to allow to setup and launch MC simulation on a simple way. It provides functionalities to: 

- Extract simple activity and attenuation maps from PET/MR images.
- Apply the BrainViset procedure to obtain realistic Activity and Attenuation maps.
- Run Analytic simulations using STIR simulation procedure and MC simulation using SimSET (comming soon).

**SETUP:** 

- Clone the repository
- Run "setup.sh" (It will ask for your sudo password. Sorry for this. Will be improved soon.)

NOTE: Monte Carlo simulations usually take a lot of space. If you want to change the default Data and Results directories you can do so in config.yml


**LAUNCH A SIMULATION**

- Open Python and import the simpet class.
- Tune the parameters of the simulation to your needs (edit "initialParams.yml" or derive your own using it as a example.)
- Create a simulation object. _EXAMPLE_ Sample Data is provided in Data/test: test_simu = simpet.SimPET('Data/test_image/testParams.yml')
- Run the simulation: test_simu.run()





