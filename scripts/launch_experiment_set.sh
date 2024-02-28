#!/bin/bash
# Variable are defined in the ENVFILE

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
SIMPET_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$SIMPET_DIR"/logs
ENVFILE="$SIMPET_DIR"/.env

mkdir -p "$LOGS_DIR"
source "$ENVFILE"
nohup $VENV -u "$SIMPET"/scripts/experiment_set.py >"$SIMPET"/logs/simulation_set.log 2>&1 &
