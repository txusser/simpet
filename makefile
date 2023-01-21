SHELL := /bin/bash
TMPDIR = /tmp
DEST_DIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
INCLUDE_DIR := ${DEST_DIR}include

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
SIMSET_DEST_DIR =  ${INCLUDE_DIR}/SimSET
SIMSET_STIR_PATCH = ${DEST_DIR}src/simset/simset_for_stir.patch
SIMSET_PATH = ${SIMSET_DEST_DIR}/2.9.2
SIMSET_LIB = ${SIMSET_PATH}/lib
SIMSET_PATH_REPLACE_FSLASH = $(shell echo ${SIMSET_PATH} | sed -e 's/\//\\\//g')
SIMSET_MKFILE = ${SIMSET_PATH}/make.files/simset.make
SIMSET_MKALL = ${SIMSET_PATH}/make_all.sh

install-simset:
	if [ ! -d ${SIMSET_DEST_DIR} ]; then\
		wget -q -P ${TMPDIR} ${SIMSET_LINK};\
		mkdir -p ${SIMSET_DEST_DIR} && tar -xvf "${SIMSET_TAR}" --directory=${SIMSET_DEST_DIR} && rm ${SIMSET_TAR};\
		cd ${SIMSET_DEST_DIR} && patch -s -p0 < ${SIMSET_STIR_PATCH};\
		sed -i 's/^\(SIMSET_PATH = \).*$$/\1${SIMSET_PATH_REPLACE_FSLASH}/' ${SIMSET_MKFILE};\
		cd ${SIMSET_PATH} && mkdir -p ${SIMSET_LIB} && bash ${SIMSET_MKALL};\
	else \
		echo "${SIMSET_DEST_DIR} already exists, run clean-simset if you really want to remove it (you will have to intall SimSET again.";\
	fi

clean-simset:
	rm -rf ${SIMSET_DEST_DIR}

clean:
	rm -rf ${INCLUDE_DIR}
