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
    icom = 'sudo pip install numpy==1.14.3'
    rsystem(icom)

    # Install Scipy
    icom = 'sudo pip install scipy==0.17.0'
    rsystem(icom)

    # Install Sklearn
    icom = 'sudo pip install scikit-learn==0.19.2'
    rsystem(icom)

    # Install Nibabel
    icom = 'sudo pip install nibabel==2.2.1'
    rsystem(icom)

    # Install Nilearn
    icom = 'sudo pip install nilearn==0.4.1'
    rsystem(icom)

    # Install FSL todo: discuss if necessary (not for commercial use license!)
    # icom = 'sudo apt -y install fsl-5.0'
    # rsystem(icom)

    # Install PIL
    icom = 'sudo apt -y install python-pil'
    rsystem(icom)

    # Install matplotlib
    icom = 'sudo python -mpip install matplotlib==2.0.0'
    rsystem(icom)

    # Install Pandas
    icom = 'sudo pip install pandas==0.23.4'
    rsystem(icom)

    # Install Statsmodels
    icom = 'sudo pip install statsmodels==0.9.0'
    rsystem(icom)

    # Install Seaborn
    icom = 'sudo pip install seaborn==0.9.0'
    rsystem(icom)

    # Install PyDicom
    icom = 'sudo pip install pydicom'
    rsystem(icom)

    # Install pdf2image
    icom = 'sudo pip install pdf2image'
    rsystem(icom)

    # Install PDFKit # TODO PDFKit not longer needed
    icom = 'sudo pip install pdfkit'
    rsystem(icom)

    # Install wkhtmltopdf (required to produce the PDF report from the HTML code)
    icom = 'sudo DEBIAN_FRONTEND=noninteractive apt-get install wkhtmltopdf -y'
    rsystem(icom)

    # icom = 'wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-i386.tar.xz'
    # rsystem(icom)
    # icom = 'tar vxf wkhtmltox-0.12.4_linux-generic-i386.tar.xz'
    # rsystem(icom)
    # icom = 'cp wkhtmltox/bin/wk* /usr/local/bin/'
    # rsystem(icom)

    # Install xvfb (required to execute wkhtmlpdf using a virtual display)
    icom = 'sudo apt -y install xvfb'
    rsystem(icom)

    # Install GDCM for PDF to DICOM convertion
    icom = 'sudo apt -y install python-gdcm'
    rsystem(icom)

    # Install dcm to nifti
    icom = 'sudo apt-get -y install dcm2niix'
    rsystem(icom)

    # Install DCMTK
    icom = 'sudo apt -y install dcmtk'
    rsystem(icom)

    # Install Zip, Unzip and Gzip
    icom = 'sudo apt -y install zip unzip gzip'
    rsystem(icom)

    # Install Nano
    icom = 'sudo apt -y install nano'
    rsystem(icom)

    # Install libraries
    icom = 'sudo apt -y install libxpm4 libxt6 libxmu6 libboost1.65-all-dev'
    rsystem(icom)

    # install libx from source because it is not available since ubuntu version 14.04
    # Download package
    dest_path = join(dest_dir, 'libxp6_1.0.2-1ubuntu1_amd64.deb')
    icom = 'wget http://archive.ubuntu.com/ubuntu/pool/main/libx/libxp/libxp6_1.0.2-1ubuntu1_amd64.deb -O %s' % dest_path
    rsystem(icom)
    # Install from source
    icom = 'sudo dpkg -i %s' % dest_path
    rsystem(icom)
    # Remove deb package
    os.remove(dest_path)

    message = 'Done with dependencies installation!'
    print(message)


def install_repo():
    """
    Download the repo from Bitbucket and cofigure it.
    :return: 
    """
    # Donwload repo
    # url_link = 'https://www.dropbox.com/s/yup6dyxo4hcta1f/neurocloud-core-1-2-0.zip?dl=0'
    url_link = 'https://www.dropbox.com/s/7swg55hncrzzex9/neurocloud-core-1-2-0.zip?dl=0'
    dest_path = join(dest_dir, 'neurocloud-core.zip')
    exe = 'wget %s -O %s' % (url_link, dest_path)
    rsystem(exe)

    # Unzip repo
    exe = 'cd %s && unzip %s && cd - > /dev/null' % (dest_dir, basename(dest_path))
    rsystem(exe)
    # Remove zip file
    # exe = 'os.remove(%s)' % dest_path
    # rsystem(exe)

    install_matlab = False
    if install_matlab:
        # Install Matlab Runtime
        exe = 'cd %s && sudo -S ./install -destinationFolder ' \
              '"/opt/MATLAB/MATLAB_Compiler_Runtime/v901/" -agreeToLicense ' \
              'yes -mode silent && cd - > /dev/null' % join(dest_dir, 'matlab')
        rsystem(exe)

    create_links = False

    if create_links:
        # Create symbolic links required by Fruticake libs and export paths
        bdir = '/usr/lib'

        org_lib = join(dest_dir, 'neurocloud-core', 'fruitcake_src', 'book', 'lib', 'libubutil.so')
        dest_lib = join(bdir, 'libubutil.so')
        exe = 'sudo ln -s %s %s' % (org_lib, dest_lib)
        rsystem(exe)

        org_lib = join(dest_dir, 'neurocloud-core', 'fruitcake_src', 'book', 'lib', 'libubspect.so')
        dest_lib = join(bdir, 'libubspect.so')
        exe = 'sudo ln -s %s %s' % (org_lib, dest_lib)
        rsystem(exe)

        org_lib = join(dest_dir, 'neurocloud-core', 'fruitcake_src', 'book', 'lib', 'libubpet.so')
        dest_lib = join(bdir, 'libubpet.so')
        exe = 'sudo ln -s %s %s' % (org_lib, dest_lib)
        rsystem(exe)

        dest_bin = join(dest_dir, 'neurocloud-core', 'fruitcake_src', 'bin')
        exe = 'chmod +x %s' % dest_bin
        rsystem(exe)

        # Set enviroment variables
        exe = 'echo PATH=\"$HOME/bin:$HOME/.local/bin:$PATH:/opt/qubiotech/neurocloud-core/fruitcake_src/bin\" >> ~/.profile'
        rsystem(exe)
        exe = 'export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:/opt/qubiotech/neurocloud-core/include/ITK/install/lib\" >> ~/.bashrc'
        rsystem(exe)
        # exe = '/bin/bash -c "source ~/.profile'
        # rsystem(exe)
        exe = '/bin/bash -c "source ~/.bashrc'
        rsystem(exe)


def check_versions():
    """
    Finds which version of each component has been installed 
    :return: 
    """
    message = "\n***** Versioning checking *****"

    # Check matplotlib
    import matplotlib
    version = matplotlib.__version__
    message = message + 'Matplotlib version is ' + str(version) + ' and should be 2.0.0'

    # Check numpy
    import numpy
    version = numpy.__version__
    message = message + '\nNumpy version is ' + str(version) + ' and should be 1.14.3'

    # Check Scipy
    import scipy
    version = scipy.__version__
    message = message + '\nScipy version is ' + str(version) + ' and should be 0.17.0'

    print(message)
    # Check SKlearn
    import sklearn
    version = sklearn.__version__
    message = message + '\nSKlearn version is ' + str(version) + ' and should be 0.19.2'

    # Check Nibabel
    import nibabel
    version = nibabel.__version__
    message = message + '\nNibabel version is ' + str(version) + ' and should be 2.2.1'

    # Check Nipype
    import nipype
    version = nipype.__version__
    message = message + 'Nipype version is ' + str(version) + ' and should be 0.13.0'

    # Check Pandas
    import pandas
    version = pandas.__version__
    message = message + '\nPandas version is ' + str(version) + ' and should be 0.23.4'

    # Check Nilearn
    import nilearn
    version = nilearn.__version__
    message = message + '\nNilearn version is ' + str(version) + ' and should be 0.4.1'

    # Check Statsmodels
    import statsmodels
    version = statsmodels.__version__
    message = message + '\nStatsmodels version is ' + str(version) + ' and should be 0.9.0'

    # Check Seaborn
    import seaborn
    version = seaborn.__version__
    message = message + '\nSeaborn version is ' + str(version) + ' and should be >=0.8.1'

    # Check PIL
    import PIL
    version = PIL.VERSION
    message = message + '\nPIL version is ' + str(version) + ' and should be 1.1.7'

    # Check PyDicom
    import pydicom
    version = pydicom.__version__
    message = message + '\nPydicom version is ' + str(version) + ' and should be >= 1.2.0'

    print(message)
    with open(log_file, 'a') as wfile:
        wfile.write(log_file)

###################################################

# Install dependencies
#install_soap()

# Install neurocloud repository
# install_repo()

# Check versioning
# check_versions()
