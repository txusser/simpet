import argparse
import yaml
import re
import math
from typing import Mapping, Any, List
from pathlib import Path


parser = argparse.ArgumentParser(description='Check ParamsOSEM3D.')
parser.add_argument("stir_hs", type=Path)
parser.add_argument("config", type=Path)
args = vars(parser.parse_args())


def finditem(obj: Mapping[str, Any], key: str):
    """
    Findd the value associated to a ``key``
    recursively in a nested ``dict``.

    Args:
        obj: ``dict``-like object.
        key: key whose value is the target.

    Returns:
        If founfd the value associated to ``key``.
    """
    if key in obj:
        return obj[key]
    for _, v in obj.items():
        if isinstance(v, dict):
            item = finditem(v, key)
            if item is not None:
                return item


def check_scanner_radius(cfg: Mapping[str, Any], stir_hs: List[str], cfg_name: str, stir_hs_name: str) -> None:
    """
    Checks if STIR's diameter is the same
    as ``2 * scanner_config`` from the configuration.

    Args:
        cfg: SIMPET config file.
        stir_hs: STIR .hs file.
    """
    stir_diameter = [param.strip("\n") for param in stir_hs if re.match("Inner ring diameter \(cm\)", param)]
    stir_diameter = float(stir_diameter.pop().rpartition(":= ")[-1])

    cfg_radius = float(finditem(cfg, "scanner_radius"))
    cfg_diameter = 2 * cfg_radius

    print(f"STIR HS: {stir_hs_name}, CFG: {cfg_name}.")
    print("Scanner diameter extracted from Inner ring diameter (cm) in .hs file")
    print(f"Scanner diameter extracted from 2 * scanner_radius -> 2 * {cfg_radius} in config file")
    if not math.isclose(cfg_diameter, stir_diameter):
        print(f"Scanner diameter differs, STIR: {stir_diameter}, CFG: {cfg_diameter}.\n")
    else:
        print(f"Scanner diameter approx. eq., STIR: {stir_diameter}, CFG: {cfg_diameter}.\n")


def check_s_total_size(cfg: Mapping[str, Any], stir_hs: List[str], cfg_name: str, stir_hs_name: str) -> None:
    """
    Checks if STIR's diameter is the same
    as ``2 * scanner_config`` from the configuration.

    Args:
        cfg: SIMPET config file.
        stir_hs: STIR .hs file.
    """
    stir_bin_size = [param.strip("\n") for param in stir_hs if re.match("Default bin size \(cm\)", param)]
    stir_bin_size = float(stir_bin_size.pop().rpartition(":= ")[-1])

    stir_s_bins = [param.strip("\n") for param in stir_hs if re.match("!matrix size \[1\]", param)]
    stir_s_bins = int(stir_s_bins.pop().rpartition(":= ")[-1])

    num_td = int(finditem(cfg, "num_td_bins"))
    scanner_radius = float(finditem(cfg, "scanner_radius"))

    print(f"STIR HS: {stir_hs_name}, CFG: {cfg_name}.")
    print(f"Config scanner_radius = {scanner_radius}, config diameter = {2 * scanner_radius}.")
    print(f"Config num_td_bins = {num_td}.")
    print(f"Config bin size -> 2 * scanner_radius / num_td = {2 * scanner_radius / num_td}.")
    print(f"s n bins extracted from !matrix size [1] ({stir_s_bins}) in .hs file")
    print(f"s bin size extracted from Default bin size (cm) ({stir_bin_size}) in .hs file")
    print(f"n_bins_s * bin_size_s = {stir_bin_size * stir_s_bins}.\n")


with open(args["stir_hs"], 'r') as stir_hs:
    stir_file = stir_hs.readlines()


with open(args["config"], 'r') as cfg:
    config = yaml.safe_load(cfg)

check_scanner_radius(config, stir_file, str(args["config"]), str(args["stir_hs"]))
check_s_total_size(config, stir_file, str(args["config"]), str(args["stir_hs"]))
