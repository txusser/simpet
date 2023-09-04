import yaml
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Diff YAML files.")
parser.add_argument("yaml-1", type=Path)
parser.add_argument("yaml-2", type=Path)

args = vars(parser.parse_args())

with open(args["yaml-1"].resolve(), "r") as f1:
    config1 = yaml.safe_load(f1)

with open(args["yaml-2"].resolve(), "r") as f2:
    config2 = yaml.safe_load(f2)

diff_keys = set(config1.keys()) - set(config2.keys())

if diff_keys:
    print(
        f"Following keys are in {args['yaml-1'].resolve().name} but not in {args['yaml-2'].resolve().name}: {diff_keys}"
    )
else:
    print("The files have the same fields.")
