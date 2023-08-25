#! /usr/bin/bash

export PATH=$PWD/include/fruitcake/bin:$PATH
export LD_LIBRARY_PATH=$PWD/include/fruitcake/book/lib:$LD_LIBRARY_PATH
export PATH=$PWD/include/format_converters:$PATH

sudo apt update -y

sudo apt install unzip libboost-dev libboost-all-dev libpcre3 libpcre3-dev libncurses-dev cmake swig

sudo apt install python3 python3-pip ipython python3-numpy python3-scipy python3-nibabel python3-matplotlib python3-pandas

pip3 install -U PyYAML nilearn nipype

python3 setup.py