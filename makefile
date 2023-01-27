SHELL := /bin/bash
TMPDIR = /tmp
DEST_DIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
INCLUDE_DIR := ${DEST_DIR}include

deps:
	sudo apt-get -y -q update ;\
	sudo apt-get install -y -q \
	software-properties-common \
	wget \
	unzip \
	sshpass \
	libboost-dev \
	libboost-all-dev \
	libpcre3 \
	libpcre3-dev \
	libncurses-dev \
	cmake \
	g++ \
	swig ;\
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CC86BB64 ;\
	sudo add-apt-repository -y ppa:rmescandon/yq ;\
	sudo apt-get -y -q update ;\
	sudo apt-get install -y -q yq

SIMSET_LINK = http://depts.washington.edu/simset/downloads/phg.2.9.2.tar.Z
SIMSET_TAR = ${TMPDIR}/phg.2.9.2.tar.Z
SIMSET_DEST_DIR =  ${INCLUDE_DIR}/SimSET
SIMSET_PATH = ${SIMSET_DEST_DIR}/2.9.2
SIMSET_BIN = ${SIMSET_PATH}/bin
SIMSET_LIB = ${SIMSET_PATH}/lib
SIMSET_MKALL = ${SIMSET_PATH}/make_all.sh
SIMSET_STIR_PATCH = ${DEST_DIR}src/simset/simset_for_stir.patch
SIMSET_MKFILE = ${SIMSET_PATH}/make.files/simset.make

install-simset:
	if [ ! -d ${SIMSET_DEST_DIR} ]; then\
		wget -q -P ${TMPDIR} ${SIMSET_LINK};\
		mkdir -p ${SIMSET_DEST_DIR} && tar -xvf "${SIMSET_TAR}" --directory=${SIMSET_DEST_DIR} && rm ${SIMSET_TAR};\
		cd ${SIMSET_DEST_DIR} && patch -s -p0 < ${SIMSET_STIR_PATCH};\
		sed -i 's/^\(SIMSET_PATH = \).*$$/\1$(subst /,\/,${SIMSET_PATH})/' ${SIMSET_MKFILE};\
		cd ${SIMSET_PATH} && mkdir -p ${SIMSET_LIB} && bash ${SIMSET_MKALL};\
	else\
		echo "${SIMSET_DEST_DIR} already exists, run clean-simset if you really want to remove it (you will have to intall SimSET again.";\
	fi

check-simset:
	declare -a simset_files=(addrandoms bin calcattenuation combinehist makeindexfile phg timesort);\
	for file in "$${simset_files[@]}"; do\
		if [ ! -f "${SIMSET_BIN}/$${file}" ]; then\
			echo "${SIMSET_BIN}/$${file} does not exists, check your installation.";\
		else\
			echo "${SIMSET_BIN}/$${file} exists.";\
		fi;\
	done

clean-simset:
	rm -rf ${SIMSET_DEST_DIR}

SIMSET_SRC = ${SIMSET_PATH}/src
SIMSET_LIBSIMSET = ${SIMSET_LIB}/libsimset.so
STIR_DEST_DIR = ${INCLUDE_DIR}/STIR/STIR
STIR_BUILD_DIR = ${INCLUDE_DIR}/STIR/build
STIR_INSTALL_DIR = ${INCLUDE_DIR}/STIR/install
STIR_INSTALL_BIN = ${STIR_INSTALL_DIR}/bin
STIR_MKFILE = ${STIR_BUILD_DIR}/CMakeCache.txt
NPROC = $(shell nproc)

install-stir:
	${MAKE} install-simset;\
	mkdir -p ${STIR_DEST_DIR} ${STIR_BUILD_DIR} ${STIR_INSTALL_DIR};\
	cd ${STIR_BUILD_DIR} && cmake ${STIR_DEST_DIR};\
	echo ${STIR_INSTALL_DIR};\
	sed -i\
		-e 's/^\(BUILD_SWIG_PYTHON\).*$$/\1:BOOL=OFF/'\
		-e 's/^\(CMAKE_INSTALL_PREFIX\).*$$/\1:PATH=$(subst /,\/,${STIR_INSTALL_DIR})/'\
		-e 's/^\(SIMSET_INCLUDE_DIRS\).*$$/\1:PATH=$(subst /,\/,${SIMSET_SRC})/'\
		-e 's/^\(SIMSET_LIBRARY\).*$$/\1:FILEPATH=$(subst /,\/,${SIMSET_LIBSIMSET})/'\
		-e 's/^\(STIR_OPENMP\).*$$/\1:BOOL=ON/'\
		${STIR_MKFILE};\
	cmake ${STIR_DEST_DIR};\
	make -s -j${NPROC};\
	make install

check-stir:
	declare -a stir_files=(FBP2D FBP3DRP forward_project lm_to_projdata OSMAPOSL zoom_image);\
	for file in "$${stir_files[@]}"; do\
		if [ ! -f "${STIR_INSTALL_BIN}/$${file}" ]; then\
			echo "${STIR_INSTALL_BIN}/$${file} does not exists, check your installation.";\
		else\
			echo "${STIR_INSTALL_BIN}/$${file} exists.";\
		fi;\
	done

clean-stir:
	rm -rf ${STIR_INSTALL_DIR} ${STIR_BUILD_DIR};\
	cd ${STIR_DEST_DIR} && git reset --hard HEAD

clean:
	${MAKE}\
		clean-simset\
		clean-stir
