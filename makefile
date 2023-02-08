SHELL := /bin/bash
TMPDIR := /tmp
ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ASSETS_DIR := ${ROOT_DIR}assets
INCLUDE_DIR := ${ROOT_DIR}include
SUBMODULES_DIR := ${ROOT_DIR}submodules

.PHONY: deps install-simset check-simset clean-simset 
.PHONY: install-stir check-stir clean-stir 
.PHONY: install-resources check-resources clean-resources 
.PHONY: config-git clean-git config-paths clean-paths 
.PHONY: dummy-data install clean help

deps:
	sudo apt-get -y -q update ;\
	sudo apt-get install -y -q \
	software-properties-common \
	git[all] \
	git-lfs \
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

SIMSET_TAR = ${ASSETS_DIR}/phg.2.9.2.tar.Z
SIMSET_DEST_DIR =  ${INCLUDE_DIR}/SimSET
SIMSET_PATH = ${SIMSET_DEST_DIR}/2.9.2
SIMSET_BIN = ${SIMSET_PATH}/bin
SIMSET_LIB = ${SIMSET_PATH}/lib
SIMSET_MKALL = ${SIMSET_PATH}/make_all.sh
SIMSET_STIR_PATCH = ${ASSETS_DIR}/simset_for_stir.patch
SIMSET_MKFILE = ${SIMSET_PATH}/make.files/simset.make

install-simset: ${SIMSET_TAR}
	if [ ! -d ${SIMSET_DEST_DIR} ]; then \
		mkdir -p ${SIMSET_DEST_DIR} && tar -xvf "${SIMSET_TAR}" --directory=${SIMSET_DEST_DIR} ;\
		cd ${SIMSET_DEST_DIR} && patch -s -p0 < ${SIMSET_STIR_PATCH} ;\
		sed -i 's/^\(SIMSET_PATH = \).*$$/\1$(subst /,\/,${SIMSET_PATH})/' ${SIMSET_MKFILE} ;\
		cd ${SIMSET_PATH} && mkdir -p ${SIMSET_LIB} && bash ${SIMSET_MKALL} ;\
	else \
		echo "${SIMSET_DEST_DIR} already exists, run clean-simset if you really want to remove it (you will have to intall SimSET again.)" ;\
	fi

check-simset:
	declare -a simset_files=(addrandoms bin calcattenuation combinehist makeindexfile phg timesort) ;\
	for file in "$${simset_files[@]}"; do \
		if [ ! -f "${SIMSET_BIN}/$${file}" ]; then \
			echo "${SIMSET_BIN}/$${file} does not exists, check your installation." ;\
		else \
			echo "${SIMSET_BIN}/$${file} exists." ;\
		fi ;\
	done

clean-simset:
	rm -rf ${SIMSET_DEST_DIR}

SIMSET_SRC = ${SIMSET_PATH}/src
SIMSET_LIBSIMSET = ${SIMSET_LIB}/libsimset.so
STIR_DIR = ${SUBMODULES_DIR}/STIR/STIR
STIR_BUILD_DIR = ${SUBMODULES_DIR}/STIR/build
STIR_INSTALL_DIR = ${SUBMODULES_DIR}/STIR/install
STIR_INSTALL_BIN = ${STIR_INSTALL_DIR}/bin
STIR_MKFILE = ${STIR_BUILD_DIR}/CMakeCache.txt
STIR_FINAL_DEST_DIR = ${INCLUDE_DIR}/STIR
NPROC = $(shell nproc)

install-stir: install-simset ${STIR_DIR}
	if [ ! -d ${STIR_FINAL_DEST_DIR} ]; then \
		mkdir -p ${STIR_BUILD_DIR} ${STIR_INSTALL_DIR} ${STIR_FINAL_DEST_DIR} ;\
		cd ${STIR_BUILD_DIR} && cmake ${STIR_DIR} ;\
		sed -i \
			-e 's/^\(BUILD_SWIG_PYTHON\).*$$/\1:BOOL=OFF/' \
			-e 's/^\(CMAKE_INSTALL_PREFIX\).*$$/\1:PATH=$(subst /,\/,${STIR_INSTALL_DIR})/' \
			-e 's/^\(SIMSET_INCLUDE_DIRS\).*$$/\1:PATH=$(subst /,\/,${SIMSET_SRC})/' \
			-e 's/^\(SIMSET_LIBRARY\).*$$/\1:FILEPATH=$(subst /,\/,${SIMSET_LIBSIMSET})/' \
			-e 's/^\(STIR_OPENMP\).*$$/\1:BOOL=ON/' \
			${STIR_MKFILE} ;\
		cmake ${STIR_DIR} ;\
		make -s -j${NPROC} ;\
		make install ;\
		mv ${STIR_BUILD_DIR} ${STIR_INSTALL_DIR} ${STIR_FINAL_DEST_DIR} ;\
	else \
		echo "${STIR_FINAL_DEST_DIR} already exists, run clean-stir if you really want to remove it (you will have to intall STIR again)." ;\
	fi

check-stir:
	declare -a stir_files=(FBP2D FBP3DRP forward_project lm_to_projdata OSMAPOSL zoom_image) ;\
	for file in "$${stir_files[@]}"; do \
		if [ ! -f "${STIR_INSTALL_BIN}/$${file}" ]; then \
			echo "${STIR_INSTALL_BIN}/$${file} does not exists, check your installation." ;\
		else \
			echo "${STIR_INSTALL_BIN}/$${file} exists." ;\
		fi ;\
	done

clean-stir:
	rm -rf ${STIR_FINAL_DEST_DIR} ;\
	cd ${STIR_DIR} && git reset --hard HEAD

RESOURCES_ZIP = ${ASSETS_DIR}/fruitcake.zip
RESOURCES_TMP = ${TMPDIR}/resources

install-resources: ${RESOURCES_ZIP}
	mkdir -p ${RESOURCES_TMP} ${INCLUDE_DIR} && unzip -o ${RESOURCES_ZIP} -d ${RESOURCES_TMP} ;\
	declare -a resources=(fruitcake format_converters) ;\
	for rce in "$${resources[@]}"; do \
		include_path="${INCLUDE_DIR}/$${rce}" ;\
		tmp_path="${RESOURCES_TMP}/$${rce}" ;\
		if [ ! -d $${include_path} ]; then \
			mv $${tmp_path} ${INCLUDE_DIR} ;\
			chmod -R +x $${include_path} ;\
		else \
			echo "$${include_path} already exists, run make clean-resources in order to clean resources installation (fruitcake will be removed as well)." ;\
		fi ;\
	done ;\
	rm -rf ${RESOURCES_TMP}

check-resources:
	declare -a resources_paths=(${FRUITCAKE_PATH} ${FORMAT_CONVERTERS_PATH}) ;\
	for path in "$${resources_paths[@]}"; do \
		if [ ! -d "$${path}" ]; then \
			echo "$${path} does not exists, clean fruitcake and format_converters with clean-resources and run install-resources." ;\
		else \
			echo "$${path} exists." ;\
		fi ;\
	done

clean-resources:
	rm -rf ${INCLUDE_DIR}/fruitcake ${INCLUDE_DIR}/format_converters

config-git:
	git config --local filter.config.smudge ${PROJECT_ROOT}scripts/smudge-config.sh
	git config --local filter.config.clean ${PROJECT_ROOT}scripts/clean-config.sh
	chmod +x -R ${PROJECT_ROOT}scripts

clean-git:
	git config --local --unset filter.config.smudge
	git config --local --unset filter.config.clean

FRUITCAKE_PATH = ${INCLUDE_DIR}/fruitcake
FRUITCAKE_BIN = ${FRUITCAKE_PATH}/bin
FRUITCAKE_LIB = ${FRUITCAKE_PATH}/book/lib
FORMAT_CONVERTERS_PATH = ${INCLUDE_DIR}/format_converters

config-paths:
	touch $${HOME}/.bashrc ;\
	declare -a simpet_paths=( \
		'export PATH=${FRUITCAKE_BIN}:$$PATH' \
		'export LD_LIBRARY_PATH=${FRUITCAKE_LIB}:$$LD_LIBRARY_PATH' \
		'export PATH=${FORMAT_CONVERTERS_PATH}:$$PATH' \
	) ;\
	for path in "$${simpet_paths[@]}"; do \
		grep -qxF "$${path}" "$${HOME}"/.bashrc || echo "$${path}" >> $${HOME}/.bashrc ;\
	done

clean-paths:
	touch "$${HOME}/.bashrc"
	sed -i \
		-e '/export PATH=$(subst /,\/,${FRUITCAKE_BIN}):$$PATH/d' \
		-e '/export LD_LIBRARY_PATH=$(subst /,\/,${FRUITCAKE_LIB}):$$LD_LIBRARY_PATH/d' \
		-e '/export PATH=$(subst /,\/,${FORMAT_CONVERTERS_PATH}):$$PATH/d' \
		"$${HOME}/.bashrc"

DATA_DIR = ${ROOT_DIR}Data
DATA_ZIP = ${ASSETS_DIR}/Data.zip

dummy-data: ${DATA_ZIP}
	if [ ! -d "${DATA_DIR}" ]; then \
		mkdir -p ${DATA_DIR} && unzip -o ${DATA_ZIP} -d ${ROOT_DIR} ;\
	else \
		echo "${DATA_DIR} already exists, remove it manually." ;\
	fi

install:
	${MAKE} \
		deps \
		install-simset \
		check-simset \
		install-stir \
		check-stir \
		install-resources \
		check-resources \
		config-paths \

clean:
	${MAKE} \
		clean-simset \
		clean-stir \
		clean-resources

help:
	@echo "Help:"
	@echo "	- deps: Install the dependencies of the projects via apt."
	@echo ""
	@echo "	- install-simset: Install SimSET with STIR patch at directory ${SIMSET_DEST_DIR}."
	@echo ""
	@echo "	- check-simset: Check that SIMSet binaries exist."
	@echo ""
	@echo "	- clean-simset: Clean SimSET installation (removes ${SIMSET_DEST_DIR} directory)."
	@echo ""
	@echo "	- install-stir: Install STIR at directory $(shell dirname ${STIR_DIR}), install-simset is a prerequisite. Set NPROC=n to use n CPU cores in compilation."
	@echo ""
	@echo "	- check-stir: Check that STIR binaries exist."
	@echo ""
	@echo "	- clean-stir: Clean STIR installation removing ${STIR_INSTALL_DIR} and ${STIR_BUILD_DIR} directories."
	@echo ""
	@echo "	- install-resources: Decompress ${RESOURCES_ZIP} and move fruitcake and format_converters to ${INCLUDE_DIR}"
	@echo ""
	@echo "	- check-resources: Checks that fruitcake and format_converters are in ${INCLUDE_DIR}."
	@echo ""
	@echo "	- clean-resources: Remove fruitcake and format_converters from ${INCLUDE_DIR}."
	@echo ""
	@echo "	- config-git: Add project filter drivers to local git configuration and make them executable."
	@echo ""
	@echo "	- clean-git : Remove project filter drivers from local git configuration."
	@echo ""
	@echo "	- config-paths: Iff not present in .bashrc, the paths of the projects will be appended to the file. If ~/.bashrc does not exists it will be created."
	@echo ""
	@echo "	- clean-paths: If the paths of the project are present in .bashrc file, they will be deleted. If ~/.bashrc does not exists it will be created."
	@echo ""
	@echo "	- dummy-data: Uncompress ${DATA_ZIP} at ${DATA_DIR} if ${DATA_DIR} does not exists."
	@echo ""
	@echo "	- install: Run all install, config and check recipes."
	@echo ""
	@echo "	- clean: Run all clean recipes."

