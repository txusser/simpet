"""
This script installs the necessary files to run simpet, including all the required dependencies.
Don't run this script if you think all the needed dependencies are already fulfilled.
"""
import os
from os.path import join, basename, exists
import shutil

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

    if exists(simset_dir):
        shutil.rmtree(simset_dir)
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

def install_stir(stir_dir,simset_dir):

    if exists(stir_dir):
        shutil.rmtree(stir_dir)
    os.makedirs(stir_dir)
    os.chdir(stir_dir)

    print("Cloning the SimSET input branch from STIR repo...")
    icom = 'git clone --single-branch --branch simset_input https://github.com/txusser/STIR.git'
    rsystem(icom)

    os.makedirs(join(stir_dir,'build'))
    os.makedirs(join(stir_dir,'install'))

    os.chdir(join(stir_dir,'build'))

    os.system('cmake ../STIR/')

    makefile = join(stir_dir, 'build','CMakeCache.txt')
    newmakefile = join(stir_dir, 'build','new_CMakeCache.txt')

    # Replacing the current directory into the makefile
    f_old = open(makefile,'r')
    f_new = open(newmakefile,'w')

    lines = f_old.readlines()
    for line in lines:
        line = line.replace('BUILD_SWIG_PYTHON:BOOL=OFF', 'BUILD_SWIG_PYTHON:BOOL=ON')
        line = line.replace('CMAKE_INSTALL_PREFIX:PATH=/usr/local', 
                            'CMAKE_INSTALL_PREFIX:PATH=%s' % join(stir_dir,'install'))
        line = line.replace('SIMSET_INCLUDE_DIRS:PATH=SIMSET_INCLUDE_DIRS-NOTFOUND', 
                            'SIMSET_INCLUDE_DIRS:PATH=%s' % join(simset_dir, '2.9.2', 'src'))
        line = line.replace('SIMSET_LIBRARY:FILEPATH=SIMSET_LIBRARY-NOTFOUND', 
                            'SIMSET_LIBRARY:FILEPATH=%s' % join(simset_dir, '2.9.2', 'lib', 'libsimset.so'))
        line = line.replace('STIR_OPENMP:BOOL=OFF', 'STIR_OPENMP:BOOL=ON')
        f_new.write(line)
    f_old.close()
    f_new.close()

    shutil.move(newmakefile,makefile)

    os.system('cmake ../STIR/')
    os.system('make -j4  & make install')

def update_config(stir_dir,simset_dir):

    configfile = 'config.yml'
    newconfigfile = 'newconfig.yml'

    # Replacing the current directory into the makefile
    f_old = open(configfile,'r')
    f_new = open(newconfigfile,'w')

    lines = f_old.readlines()
    for line in lines:
        if line.startswith('dir_stir'):
            line = ('dir_stir:  "%s"' % stir_dir)
        if line.startswith('dir_simset'):
            line = ('dir_simset:  "%s"' % simset_dir)
        f_new.write(line)
    f_old.close()
    f_new.close()

    shutil.move(newconfigfile,configfile)

def install_soap():
    """
    Execute installation of all dependencies
    :return:
    """
    # Install SOAP

    icom = 'sudo apt install libboost-dev libboost-all-dev'
    rsystem(icom)

    icom = 'sudo apt install libpcre3 libpcre3-dev'
    rsystem(icom)

    # Install and upgrade PIP
    icom = 'sudo apt install python-yaml'
    rsystem(icom)

    # Install numpy
    icom = 'sudo apt install python-numpy'
    rsystem(icom)

    # Install Scipy
    icom = 'sudo apt install python-scipy'
    rsystem(icom)

    # Install Nibabel
    icom = 'sudo apt install python-nibabel'
    rsystem(icom)

    # Install matplotlib
    icom = 'sudo apt install python-matplotlib'
    rsystem(icom)

    # Install Pandas
    icom = 'sudo apt install python-pandas'
    rsystem(icom)

# Extract Resources
command = 'tar -xvf resources.tar.xz'
rsystem(command)

# Fruitcake is not needed right now
# # Add fruitcake paths to bashrc... This can be a problem...
#fruitcake_binpath = 'echo PATH=%s/fruitcake/bin:$PATH" >> ~/.bashrc'
#rsystem(fruitcake_binpath)

# fruitcake_ldpath = 'echo LD_LIBRARY_PATH=%s/fruitcake/book/lib:$LD_LIBRARY_PATH" >> ~/.bashrc'
# rsystem(fruitcake_ldpath)

install_soap()

simpet_dir = os.getcwd()
os.chdir(dest_dir)

simset_dir = join(dest_dir,"SimSET")
install_simset(simset_dir)

stir_dir = join(dest_dir,"STIR")
install_stir(stir_dir, simset_dir)

os.chdir(simpet_dir)
update_config




