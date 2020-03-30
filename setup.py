"""
This script installs the necessary files to run simpet, including all the required dependencies.
Don't run this script if you think all the needed dependencies are already fulfilled.
"""
import os
from os.path import join, basename, exists
import shutil
from multiprocessing import cpu_count

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
        print("OK executing: %s" % command)
        with open(log_file, 'a') as w_file:
            w_file.write(message)

def install_simset(simset_dir, log_file):

    if exists(simset_dir):
        shutil.rmtree(simset_dir)
    os.makedirs(simset_dir)

    # Download, patch and compile SimSET
    print('Downloading SimSET source from Washington University repos...')
    icom = 'wget -q http://depts.washington.edu/simset/downloads/phg.2.9.2.tar.Z > %s' % log_file
    rsystem(icom)
    icom = 'tar -xvf %s/phg.2.9.2.tar.Z --directory=SimSET > %s' % (dest_dir,log_file)
    rsystem(icom)
    os.remove('phg.2.9.2.tar.Z')

    os.chdir(simset_dir)

    #Let's Apply the SimSET patch for SimPET
    print('Applying modification patch for SimSET-STIR interface...')
    icom = 'patch -s -p0 < %s/src/simset/simset_for_stir.patch' % simpet_dir
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
    print('Compiling SimSET...')
    icom = './make_all.sh'
    rsystem(icom)

    print('Verifying installation...')
    verify_simset_install(simset_dir)

def verify_simset_install(simset_dir):

    if exists(join(simset_dir,'2.9.2','lib','libsimset.so')):
        print('SimSET library: OK')
    else:
        raise Exception('Failed to build SimSET')

    bin_dir = join(simset_dir,'2.9.2','bin')

    checks = ['addrandoms', 'bin', 'calcattenuation', 'combinehist', 'makeindexfile', 'phg', 'timesort']

    for i in checks:

        if exists(join(bin_dir,i)):
            print('%s: OK' % i)
        else:
           raise Exception('Failed to build %s' % i)

def install_stir(stir_dir, simset_dir, log_file):

    build_dir = join(stir_dir,'build')
    install_dir = join(stir_dir,'install')

    if exists(stir_dir):
        shutil.rmtree(stir_dir)

    os.makedirs(stir_dir)
    os.makedirs(build_dir)
    os.makedirs(install_dir)
    os.chdir(stir_dir)
    print("Cloning the SimSET input branch from STIR repo...")
    icom = 'git clone --single-branch --branch simset_input https://github.com/txusser/STIR.git'
    rsystem(icom)

    os.chdir(build_dir)
    rsystem('cmake ../STIR/')

    makefile = join(build_dir,'CMakeCache.txt')
    newmakefile = join(stir_dir, 'build','new_CMakeCache.txt')

    # Replacing the current directory into the makefile
    f_old = open(makefile,'r')
    f_new = open(newmakefile,'w')

    lines = f_old.readlines()
    for line in lines:
        if line.startswith('BUILD_SWIG_PYTHON'):
            line = 'BUILD_SWIG_PYTHON:BOOL=OFF\n'
        if line.startswith('CMAKE_INSTALL_PREFIX'):
            line = ('CMAKE_INSTALL_PREFIX:PATH=%s\n' % install_dir)
        if line.startswith('SIMSET_INCLUDE_DIRS'):
            line = ('SIMSET_INCLUDE_DIRS:PATH=%s\n' % join(simset_dir, '2.9.2', 'src'))
        if line.startswith('SIMSET_LIBRARY'):
            line = ('SIMSET_LIBRARY:FILEPATH=%s\n' % join(simset_dir, '2.9.2', 'lib', 'libsimset.so'))
        if line.startswith('STIR_OPENMP'):
            line = 'STIR_OPENMP:BOOL=ON'
        f_new.write(line)

    f_old.close()
    f_new.close()

    shutil.move(newmakefile,makefile)
    rsystem('cmake ../STIR/')

    print('Building STIR....')
    icom = 'make -s -j%s & make install' % str(cpu_count())
    rsystem(icom)

def update_config(stir_dir,simset_dir):

    configfile = 'config.yml'
    newconfigfile = 'newconfig.yml'

    # Replacing the current directory into the makefile
    f_old = open(configfile,'r')
    f_new = open(newconfigfile,'w')

    lines = f_old.readlines()
    for line in lines:
        if line.startswith('dir_stir'):
            line = ('dir_stir:  "%s"\n' % join(stir_dir,'install'))
        if line.startswith('dir_simset'):
            line = ('dir_simset:  "%s"\n' % join(simset_dir,'2.9.2'))
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

    icom = 'sudo apt install python -y -q'
    rsystem(icom)

    icom = 'sudo apt install python-pip -y -q'
    rsystem(icom)

    icom = 'sudo apt install libboost-dev libboost-all-dev -y -q'
    rsystem(icom)

    icom = 'sudo apt install libpcre3 libpcre3-dev -y -q'
    rsystem(icom)

    icom = 'sudo apt install libncurses-dev -y -q'
    rsystem(icom)

    # Install and upgrade PIP
    icom = 'sudo pip install --ignore-installed PyYAML==5.1 '
    rsystem(icom)

    # Update yaml to use FullLoader
    #icom = 'sudo pip install -U pyYAML'
    #rsystem(icom)

    # Install numpy
    icom = 'sudo apt install python-numpy -y -q'
    rsystem(icom)

    # Install Scipy
    icom = 'sudo apt install python-scipy -y -q'
    rsystem(icom)

    # Install Nibabel
    icom = 'sudo apt install python-nibabel -y -q'
    rsystem(icom)

    # Install matplotlib
    icom = 'sudo apt install python-matplotlib -y -q'
    rsystem(icom)

    # Install Pandas
    icom = 'sudo apt install python-pandas -y -q'
    rsystem(icom)

    # Install cmake (needed for STIR)
    icom = 'sudo apt install cmake -y -q'
    rsystem(icom)

    # Install swig (needed for STIR)
    icom = 'sudo apt install swig -y -q'
    rsystem(icom)

# Extract Resources
print('Extracting resources...')
command = 'tar -xvf resources.tar.xz'
rsystem(command)

# Fruitcake is not needed right now
# # Add fruitcake paths to bashrc... This can be a problem...
# fruitcake_binpath = 'echo "export PATH=%s/fruitcake/bin:$PATH" >> ~/.bashrc' % dest_dir
# rsystem(fruitcake_binpath)

# fruitcake_ldpath = 'echo "export LD_LIBRARY_PATH=%s/fruitcake/book/lib:$LD_LIBRARY_PATH" >> ~/.bashrc' % dest_dir
# rsystem(fruitcake_ldpath)

# rsystem('source ~/.bashrc')

install_soap()

simpet_dir = os.getcwd()
os.chdir(dest_dir)

simset_dir = join(dest_dir,"SimSET")
install_simset(simset_dir, log_file)

stir_dir = join(dest_dir,"STIR")
install_stir(stir_dir, simset_dir, log_file)

os.chdir(simpet_dir)
update_config(stir_dir,simset_dir)
