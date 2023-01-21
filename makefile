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
