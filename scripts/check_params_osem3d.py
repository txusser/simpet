import argparse
from pathlib import Path
from enum import Enum


class OSEM3DParams(Enum):
    OBJECTIVE_FUNCTION_TYPE = "objective function type"
    POISSONLOGLIKELIHOODWITHLINEARMODELFORMEANANDPROJDATA_PARAMETERS = "PoissonLogLikelihoodWithLinearModelForMeanAndProjData Parameters"
    MAXIMUM_ABSOLUTE_SEGMENT_NUMBER_TO_PROCESS = "maximum absolute segment number to process"
    ZERO_END_PLANES_OF_SEGMENT_0 = "zero end planes of segment 0"
    SENSITIVITY_FILENAME = "sensitivity filename"
    RECOMPUTE_SENSITIVITY = "recompute sensitivity"
    USE_SUBSET_SENSITIVITIES = "use subset sensitivities"
    PROJECTOR_PAIR_TYPE = "projector pair type"
    PROJECTOR_PAIR_USING_MATRIX_PARAMETERS = "Projector Pair Using Matrix Parameters"
    MATRIX_TYPE = "Matrix type"
    RAY_TRACING_MATRIX_PARAMETERS = "Ray tracing matrix parameters"
    NUMBER_OF_RAYS_IN_TANGENTIAL_DIRECTION_TO_TRACE_FOR_EACH_BIN = "number of rays in tangential direction to trace for each bin"
    PRIOR_TYPE = "prior type"
    FILTERROOTPRIOR_PARAMETERS = "FilterRootPrior Parameters"
    PENALISATION_FACTOR = "penalisation factor"
    FILTER_TYPE = "Filter type"
    MEDIAN_FILTER_PARAMETERS = "Median Filter Parameters"
    MASK_RADIUS_X = "mask radius x"
    MASK_RADIUS_Y = "mask radius y"
    MASK_RADIUS_Z = "mask radius z"
    ZOOM = "zoom"
    XY_OUTPUT_IMAGE_SIZE_IN_PIXELS = "xy output image size (in pixels)"
    Z_OUTPUT_IMAGE_SIZE_IN_PIXELS = "Z output image size (in pixels)"
    NUMBER_OF_SUBSETS = "number of subsets"
    NUMBER_OF_SUBITERATIONS = "number of subiterations"
    SAVE_ESTIMATES_AT_SUBITERATION_INTERVALS = "save estimates at subiteration intervals"
    ENFORCE_INITIAL_POSITIVITY_CONDITION = "enforce initial positivity condition"
    OUTPUT_FILENAME_PREFIX = "output filename prefix"


parser = argparse.ArgumentParser(description='Check ParamsOSEM3D.')
parser.add_argument("params_file", type=Path)
args = vars(parser.parse_args())

must_have_params = set(param.value for param in OSEM3DParams)

with open(args["params_file"], 'r') as pfile:
    lines = pfile.readlines()

file_params = [line.rpartition(":")[0].strip(" ") for line in lines]
file_params = set(param for param in file_params if param)

missing_params = must_have_params - must_have_params.intersection(file_params)

print("OSEM3D must have params:\n")
print(*list(must_have_params), sep="\n")
print(f"\nMising params in {str(args['params_file'])}: {missing_params}.")
