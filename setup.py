"""
This script installs the necessary files to run simpet, including all the required dependencies.
Don't run this script if you think all the needed dependencies are already fulfilled.
"""
import os
from os.path import join, basename, exists
import shutil

simpet_dir = os.getcwd()
dest_dir = join(os.getcwd(), 'include')
log_file = join(dest_dir, 'log_setup.txt')

def rsystem(command):
    """
    Executes command, raise an error if it fails and send status to logfile
    :param command: (string) command to be executed
    :return: 
    """

    message = "\nEXE: %s" % command
    print(message)
    
    if os.system(command) != 0:
        message = "ERROR executing: %s " % command
        with open(log_file, 'a') as w_file:
            w_file.write(message)
        raise TypeError(command)
    else:
        print "OK executing: %s" % command
        with open(log_file, 'a') as w_file:
            w_file.write(message)

def install_simset(simset_dir):

    if not exists(simset_dir):
        os.makedirs(simset_dir)

    # Download, patch and compile SimSET
    icom = 'wget http://depts.washington.edu/simset/downloads/phg.2.9.2.tar.Z'
    rsystem(icom)
    icom = 'tar -xvf %s/phg.2.9.2.tar.Z --directory=SimSET' % dest_dir
    rsystem(icom)
    os.remove('phg.2.9.2.tar.Z')

    os.chdir(simset_dir)

    #Let's Apply the SimSET patch for SimPET
    icom = 'patch -s -p0 < ~/Work/repositories/simpet/src/simset/simset_for_stir.patch'
    rsystem(icom)

    makefile = join(simset_dir, '2.9.2','make.files','simset.make')
    newmakefile = join(simset_dir, '2.9.2','make.files','simset.make.new')

    # Replacing the current directory into the makefile
    f_old = open(makefile,'r')
    f_new = open(newmakefile,'w')

    lines = f_old.readlines()
    for line in lines:
        line = line.replace('/Users/useruser/Desktop', simset_dir)
        f_new.write(line)
    f_old.close()
    f_new.close()

    shutil.move(newmakefile,makefile)

    #Now we can compile
    os.chdir(join(simset_dir,'2.9.2'))
    os.makedirs('lib')
    icom = './make_all.sh'
    rsystem(icom)

def install_stir(stir_dir):

    print ("To be done....")

def install_soap():
    """
    Execute installation of all dependencies
    :return: 
    """
    # Install SOAP

    # Install and upgrade PIP
    icom = 'sudo apt -y install python-pip'
    rsystem(icom)
    icom = 'pip install --upgrade pip'
    rsystem(icom)

    # Install numpy
    icom = 'sudo pip install numpy'
    rsystem(icom)

    # Install Scipy
    icom = 'sudo pip install scipy'
    rsystem(icom)

    # Install Nibabel
    icom = 'sudo pip install nibabel'
    rsystem(icom)

    # Install Nilearn
    icom = 'sudo pip install nilearn'
    rsystem(icom)

    # Install matplotlib
    icom = 'sudo python -mpip install matplotlib'
    rsystem(icom)

    # Install Pandas
    icom = 'sudo pip install pandas'
    rsystem(icom)

# Extract Resources
# command = 'tar -xvf resources.tar.xz'
# rsystem(command)

# # Add fruitcake paths to bashrc...
# fruitcake_binpath = 'echo PATH=%s/fruitcake/bin:$PATH" >> ~/.bashrc'
# rsystem(fruitcake_binpath)

# fruitcake_ldpath = 'echo LD_LIBRARY_PATH=%s/fruitcake/book/lib:$LD_LIBRARY_PATH" >> ~/.bashrc'
# rsystem(fruitcake_ldpath)

simpet_dir = os.getcwd()
dest_dir = join(os.getcwd(), 'include')
log_file = join(dest_dir, 'log_setup.txt')
os.chdir(dest_dir)

simset_dir = join(dest_dir,"SimSET")
install_simset(simset_dir)