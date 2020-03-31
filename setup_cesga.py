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
        print "OK executing: %s" % command
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

def download_resources():

    print('Downloading resources from Onedrive...')
    icom = 'wget "https://onedrive.live.com/download?cid=82E5E66193A2F2B1&resid=82E5E66193A2F2B1%21145313&authkey=AD790Ox5lhx16g4"'
    rsystem(icom)
    print('Moving and extracting resources...')
    icom = 'mv download\?cid\=82E5E66193A2F2B1\&resid\=82E5E66193A2F2B1\!145313\&authkey\=AD790Ox5lhx16g4 resources.tar.gz'
    rsystem(icom)
    icom = 'tar -xvf resources.tar.xz'
    rsystem(icom)





simpet_dir = os.getcwd()
download_resources()

fruitcake_binpath = 'echo "export PATH=%s/resources/fruitcake/bin:$PATH" >> ~/.bashrc' % simpet_dir
rsystem(fruitcake_binpath)

fruitcake_ldpath = 'echo "export LD_LIBRARY_PATH=%s/resources/fruitcake/book/lib:$LD_LIBRARY_PATH" >> ~/.bashrc' % simpet_dir
rsystem(fruitcake_ldpath)

rsystem('source ~/.bashrc')

os.chdir(dest_dir)

simset_dir = join(dest_dir,"SimSET")
install_simset(simset_dir, log_file)

stir_dir = join(dest_dir,"STIR")
install_stir(stir_dir, simset_dir, log_file)

os.chdir(simpet_dir)
update_config(stir_dir,simset_dir)
