SHELL := /bin/bash
packages: 
	sudo apt-get install -y -q \
	unzip \
	sshpass \
	libboost-dev \
	libboost-all-dev \
	libpcre3 \
	libpcre3-dev \
	libncurses-dev \
	#cmake \
	swig
