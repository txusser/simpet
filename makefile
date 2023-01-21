SHELL := /bin/bash
TMPDIR = /tmp
SIMPET_DIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
INCLUDE_DIR := ${SIMPET_DIR}include

packages:
	sudo apt-get install -y -q \
	wget \
	unzip \
	sshpass \
	libboost-dev \
	libboost-all-dev \
	libpcre3 \
	libpcre3-dev \
	libncurses-dev \
	cmake \
	swig

SIMSET_LINK = http://depts.washington.edu/simset/downloads/phg.2.9.2.tar.Z
SIMSET_TAR = ${TMPDIR}/phg.2.9.2.tar.Z
SIMSET_DIR =  ${INCLUDE_DIR}/SimSET
SIMSET_STIR_PATCH = ${SIMPET_DIR}src/simset/simset_for_stir.patch
SIMSET_PATH = ${SIMSET_DIR}/2.9.2
SIMSET_LIB = ${SIMSET_PATH}/lib
SIMSET_MKFILE = ${SIMSET_PATH}/make_all.sh
SIMSET_PATH_REPLACE_FSLASH = $(shell echo ${SIMSET_PATH} | sed -e 's/\//\\\//g')
SIMSET_MKFILE = ${SIMSET_PATH}/make.files/simset.make
SIMSET_MKALL = ${SIMSET_PATH}/make_all.sh
simset:
	wget -q -P ${TMPDIR} ${SIMSET_LINK}
	mkdir -p ${SIMSET_DIR} && tar -xvf ${SIMSET_TAR} --directory=${SIMSET_DIR} && rm ${SIMSET_TAR}
	cd ${SIMSET_DIR} && patch -s -p0 < ${SIMSET_STIR_PATCH}
	sed -i 's/^\(SIMSET_PATH = \).*$$/\1${SIMSET_PATH_REPLACE_FSLASH}/' ${SIMSET_MKFILE}
	cd ${SIMSET_PATH} && mkdir -p ${SIMSET_LIB} && bash ${SIMSET_MKALL}

clean:
	rm -rf ${INCLUDE_DIR}
