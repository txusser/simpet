# SimPET

The SIMPET project is intended to provide a framework to set up and launch MC simulations in a simple way. It provides functionalities to: 

- Launch a simulation based on your activity and attenuation maps. 
- Extract realistic activity and attenuation maps from real-subject PET/MR/CT images using the BrainViset methodology.
- Quickly define new scanners for simulations using YAML files (see scanners dir inside the repository. 

## SETUP: 

- Clone the repository
- Run "setup.sh" (It will ask for your sudo password. Sorry for this. Will be improved soon.)
- After setup, a file named *simpet_paths.sh* should have been created. Consider adding the content of this file to your .bashrc. Alternatively, you can source this file each time you want to use SimPET.

## CONSIDERATIONS:
- Monte Carlo simulations usually take a lot of space. If you want to change the default Data and Results directories you can do so in *config.yml*

## LAUNCH A SIMULATION

- Open Python and import the simpet class.
- Tune the parameters of the simulation to your needs (edit "Params_template.yml" or derive your own using it as an example.)
- Create a simulation object. _EXAMPLE_  Data is provided in Data/test: test_simu = simpet.SimPET('Params_test.yml')
- Run the simulation: test_simu.run()

## CONTRIBUTORS
_Jesús Silva-Rodríguez_ 
_Pablo Aguiar_
_Aida Ninyerola-Baizan_
_Yeremaya Póveda_
_Francisco Javier López-González_
_‪Nikos Efthimiou‬_
_Arnau Farre_



