

sudo apt update -y && sudo apt upgrade -y -q

sudo apt install gcc g++ make  cmake cmake-curses-gui libx11-dev libpng-dev tcsh -y -q

sudo apt install python python-dev python-numpy ipython python-matplotlib mayavi2 -y -q

sudo apt install mpi-default-dev mpi-default-bin libinsighttoolkit4-dev libtiff5-dev -y -q

sudo apt install unzip libboost-dev libboost-all-dev libpcre3 libpcre3-dev libncurses-dev swig -y -q

sudo apt install python3 python3-pip python3-ipython python3-numpy python3-scipy python3-nibabel python3-matplotlib python3-pandas -y -q

pip3 install -U PyYAML nilearn nipype

export PATH=$PWD/include/fruitcake/bin:$PATH
export LD_LIBRARY_PATH=$PWD/include/fruitcake/book/lib:$LD_LIBRARY_PATH
export PATH=$PWD/include/format_converters:$PATH

python3 setup.py