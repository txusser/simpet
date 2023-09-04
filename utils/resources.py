import os
from os.path import abspath, join, dirname

# Ablotue paths to folders with resources used
RESOURCES = abspath(join(dirname(dirname(abspath(__file__))), "resources"))
BIN = abspath(join(dirname(dirname(abspath(__file__))), "include", "format_converters"))
FRUTICAKE = abspath(
    join(dirname(dirname(abspath(__file__))), "include", "fruitcake", "bin")
)


def get_rsc(resource, type):
    """
    Returns the absolute path to the required resource needed by SimPET
    Paths defined here include routes to resources that could be used for any
    :param resource: resource to be used
    :param type: type or resource
    :return:

    Type os resources can be:
    1) image
    2) exe

    """
    rpath = False

    ### Templates
    if type == "image":
        if resource == "tpm_file":
            rpath = join(RESOURCES, "TPM.nii")
        elif resource == "hammers":
            rpath = join(RESOURCES, "hammers.img")
        elif resource == "hammers_csv":
            rpath = join(RESOURCES, "hammers.csv")
        else:
            rpath = False

    ### Conversion tools
    elif type == "exe":
        if resource == "nii2analyze":
            rpath = join(BIN, "niitoanalyze")
        elif resource == "analyze2nii":
            rpath = join(BIN, "analyzetonii")
        else:
            rpath = False

    ### Fruitcake tools
    elif type == "fruitcake":
        if resource == "overlap":
            rpath = join(FRUTICAKE, "overlap_fraction_stats_rois")
        elif resource == "overlap_array":
            rpath = join(FRUTICAKE, "get_overlap_stats_rois_array")
        elif resource == "change_format":
            rpath = join(FRUTICAKE, "cambia_formato_hdr")
        elif resource == "change_values":
            rpath = join(FRUTICAKE, "cambia_valores_ima_hdr")
        elif resource == "change_values_array":
            rpath = join(FRUTICAKE, "change_values_array")
        elif resource == "change_interval":
            rpath = join(FRUTICAKE, "cambia_valores_de_un_intervalo")
        elif resource == "operate_image":
            rpath = join(FRUTICAKE, "opera_imagen_hdr")
        elif resource == "compute_roi_hemis_vol":
            rpath = join(FRUTICAKE, "compute_roi_hemis_volume")
        elif resource == "change_img_matrix":
            rpath = join(FRUTICAKE, "cambia_matriz_imagen_hdr")
        elif resource == "erase_negs":
            rpath = join(FRUTICAKE, "elimina_valores_negativos_hdr")
        elif resource == "erase_nans":
            rpath = join(FRUTICAKE, "elimina_valores_nan_hdr")
        elif resource == "histo_image":
            rpath = join(FRUTICAKE, "histograma_ima_hdr")
        elif resource == "rois_vols":
            rpath = join(FRUTICAKE, "compute_roi_vol_array")
        elif resource == "calc_vm_voi":
            rpath = join(FRUTICAKE, "calcula_vm_en_roi")
        elif resource == "calc_vmax_voi":
            rpath = join(FRUTICAKE, "calcula_vmax_en_roi")
        elif resource == "clustering_spm":
            rpath = join(FRUTICAKE, "generate_SPM_maps")
        elif resource == "clustering_spm":
            rpath = join(FRUTICAKE, "generate_SPM_maps")
        elif resource == "conv_sino2proy":
            rpath = join(FRUTICAKE, "conv_sino2proy")
        elif resource == "conv_proy2sino":
            rpath = join(FRUTICAKE, "conv_proy2sino")
        elif resource == "gen_hdr":
            rpath = join(FRUTICAKE, "gen_hdr")
        elif resource == "convolucion_hdr":
            rpath = join(FRUTICAKE, "convolucion_hdr")
        elif resource == "corta_pega_filcol_hdr":
            rpath = join(FRUTICAKE, "corta_pega_filcol_hdr")

        else:
            rpath = False

    if os.path.exists(str(rpath)):
        return rpath
    else:
        message = (
            "Error: Resource " + str(resource) + " of type " + str(type) + " not found!"
        )
        raise TypeError(message)
