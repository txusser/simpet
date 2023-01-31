#!/bin/bash

export GIT_DIR="$(git root)"
export INCLUDE_DIR="${GIT_DIR}/include"
export SIMSET_DIR="${INCLUDE_DIR}/SimSET/2.9.2"
export STIR_DIR="${INCLUDE_DIR}/STIR/install"

yq eval \
    '.dir_stir = strenv(STIR_DIR) |
    .dir_simset = strenv(SIMSET_DIR)' -

