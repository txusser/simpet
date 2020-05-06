#!/bin/python3

echo "Launching a simulation from cesga..."
params_file = $1
config_file = $2
simnum = $3

cat << EOF > pyscript_$simnum.py
#!/usr/bin/python3
import simpet
import subprocess
simu = simpet.SimPET(subprocess.call(["echo","$params_file"]),subprocess.call(["echo","$config_file"]))
simu.run()

EOF

chmod 755 pyscript_$simnum.py
./pyscript_$simnum.py