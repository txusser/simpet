#!/bin/bash
# Variable are defined in the ENVFILE

ENVFILE="$SIMPET"/.env

mkdir -p "$SIMPET"/logs
source "$ENVFILE"
nohup $VENV -u "$SIMPET"/scripts/experiment_set.py >"$SIMPET"/logs/simulation_set.log 2>&1 &
