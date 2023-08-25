"""
This script installs the necessary files to run simpet, including all the required dependencies.
Don't run this script if you think all the needed dependencies are already fulfilled.
"""
import os
from os.path import join, basename, exists
import shutil
from multiprocessing import cpu_count


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
    icom = 'tar -xvf %s/phg.2.9.2.tar.Z --directory=SimSET > %s' % (dest_dir, log_file)
    rsystem(icom)
    os.remove('phg.2.9.2.tar.Z')

    os.chdir(simset_dir)

    # Let's Apply the SimSET patch for SimPET
    print('Applying modification patch for SimSET-STIR interface...')
    icom = 'patch -s -p0 < %s/src/simset/simset_for_stir.patch' % simpet_dir
    rsystem(icom)

    makefile = join(simset_dir, '2.9.2', 'make.files', 'simset.make')
    newmakefile = join(simset_dir, '2.9.2', 'make.files', 'simset.make.new')

    # Replacing the current directory into the makefile
    f_old = open(makefile, 'r')
    f_new = open(newmakefile, 'w')

    lines = f_old.readlines()
    for line in lines:
        line = line.replace('/Users/useruser/Desktop', simset_dir)
        f_new.write(line)
    f_old.close()
    f_new.close()

    shutil.move(newmakefile, makefile)

    # Now we can compile
    os.chdir(join(simset_dir, '2.9.2'))
    os.makedirs('lib')
    print('Compiling SimSET...')
    icom = './make_all.sh'
    rsystem(icom)


def verify_simset_install(simset_dir):
    print('\nVerifying SIMSET installation...')
    if exists(join(simset_dir, '2.9.2', 'lib', 'libsimset.so')):
        print('SimSET library: OK')
    else:
        raise Exception('Failed to build SimSET')

    bin_dir = join(simset_dir, '2.9.2', 'bin')

    checks = ['addrandoms', 'bin', 'calcattenuation', 'combinehist', 'makeindexfile', 'phg', 'timesort']

    for i in checks:

        if exists(join(bin_dir, i)):
            print('%s: OK' % i)
        else:
            raise Exception('Failed to build %s' % i)


def install_stir(stir_dir, simset_dir, log_file):
    build_dir = join(stir_dir, 'build')
    install_dir = join(stir_dir, 'install')

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

    makefile = join(build_dir, 'CMakeCache.txt')
    newmakefile = join(stir_dir, 'build', 'new_CMakeCache.txt')

    # Replacing the current directory into the makefile
    f_old = open(makefile, 'r')
    f_new = open(newmakefile, 'w')

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

    shutil.move(newmakefile, makefile)
    rsystem('cmake ../STIR/')

    print('Building STIR....')
    icom = 'make -s -j%s & make install' % str(cpu_count())
    rsystem(icom)


def verify_stir_install(stir_dir):
    print('\nVerifying STIR installation...')

    bin_dir = join(stir_dir, 'install', 'bin')

    checks = ['FBP2D', 'FBP3DRP', 'forward_project', 'lm_to_projdata', 'OSMAPOSL', 'zoom_image']

    for i in checks:

        if exists(join(bin_dir, i)):
            print('%s: OK' % i)
        else:
            raise Exception('Failed to build %s' % i)


def download_resources(dest_dir):
    print('Downloading resources from Onedrive...')
    icom = 'wget https://github.com/txusser/simpet/raw/develop/assets/Data.zip'
    rsystem(icom)
    icom = 'unzip -o Data.zip'
    rsystem(icom)

    if exists('Data.zip'):
        os.remove('Data.zip')

    icom = 'wget https://github.com/txusser/simpet/raw/develop/assets/fruitcake.zip'
    rsystem(icom)
    icom = 'unzip -o fruitcake.zip'
    rsystem(icom)
    shutil.move("fruitcake", '%s/fruitcake' % dest_dir)
    shutil.move("format_converters", '%s/format_converters' % dest_dir)

    if exists('fruitcake.zip'):
        os.remove('fruitcake.zip')


def update_config(stir_dir, simset_dir, dest_dir):
    configfile = 'config.yml'
    newconfigfile = 'newconfig.yml'

    # Replacing the current directory into the makefile
    f_old = open(configfile, 'r')
    f_new = open(newconfigfile, 'w')

    lines = f_old.readlines()
    for line in lines:
        if line.startswith('dir_stir'):
            line = ('dir_stir:  "%s"\n' % join(stir_dir, 'install'))
        if line.startswith('dir_simset'):
            line = ('dir_simset:  "%s"\n' % join(simset_dir, '2.9.2'))
        f_new.write(line)
    f_old.close()
    f_new.close()

    shutil.move(newconfigfile, configfile)

    pathfile = 'simpet_paths.sh'
    f_paths = open(pathfile, 'w')
    f_paths.write("export PATH=%s/fruitcake/bin:$PATH\n" % dest_dir)
    f_paths.write("export LD_LIBRARY_PATH=%s/fruitcake/book/lib:$LD_LIBRARY_PATH\n" % dest_dir)
    f_paths.write("export PATH=%s/format_converters:$PATH\n" % dest_dir)

    f_paths.close()

    icom = 'chmod +x %s/fruitcake/bin/*' % dest_dir
    rsystem(icom)
    icom = 'chmod +x %s/format_converters' % dest_dir
    rsystem(icom)


def verify_test_simulation(simpet_dir):
    print('\nVerifying test simulation...')
    import nibabel as nib
    import numpy as np

    results_dir = join(simpet_dir, 'Results', 'Test', 'SimSET_Sim_Discovery_ST', 'division_0')

    checks = ['trues.hdr', 'scatter.hdr', 'randoms.hdr']

    for i in checks:
        file_ = join(results_dir, i)
        if exists(file_):
            img_d = nib.load(file_).get_fdata()
            counts = np.sum(img_d)
            print("Counts in %s: %s" % (i,counts))

        else:
            raise Exception('Failed to build %s' % i)

    results_dir = join(simpet_dir, 'Results', 'Test', 'SimSET_Sim_Discovery_ST', 'OSEM3D')

    checks = ['rec_OSEM3D_32.v', 'rec_OSEM3D_32.hv']
    for i in checks:
        file_ = join(results_dir, i)
        if exists(file_):
            print('%s: OK' % i)
        else:
            raise Exception('Failed to reconstruct %s' % i)


# Setup run lines
simpet_dir = os.getcwd()
log_file = join(simpet_dir, 'log_setup.txt')
if exists(log_file):
    os.remove(log_file)

dest_dir = join(simpet_dir, 'include')
if not exists(dest_dir):
    os.makedirs(dest_dir)
os.chdir(dest_dir)

simset_dir = join(dest_dir, "SimSET")
install_simset(simset_dir, log_file)
verify_simset_install(simset_dir)

stir_dir = join(dest_dir, "STIR")
install_stir(stir_dir, simset_dir, log_file)
verify_stir_install(stir_dir)

os.chdir(simpet_dir)
download_resources(dest_dir)
update_config(stir_dir, simset_dir, dest_dir)

print("\nEverything looks good... we will launch a quick simulation now just to be sure...")
print("This can take a bit, maybe 15 min... you may abort it if you are very sure what you are doing.\n")

import simpet

test = simpet.SimPET('Data/test_image/testParams.yml')
test.run()

verify_test_simulation(simpet_dir)

print("\nNice! It seems that we are good to go. Consider adding the lines in simpet_paths.sh to your .bashrc. Enjoy SimPET!.")

