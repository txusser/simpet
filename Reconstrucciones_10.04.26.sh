#!/bin/bash

echo "=============================="
echo "Iniciando Reconstrucciones..."
echo "=============================="

#!/bin/bash


configs=(
config_test_wholebody_reference_eppendorff_C
config_test_wholebody_reference_eppendorff_D
config_test_wholebody_test_1_A
config_test_wholebody_test_1_B
config_test_wholebody_test_1_C
config_test_wholebody_test_1_D
config_test_wholebody_test_9_A
config_test_wholebody_test_9_B
config_test_wholebody_test_9_C
config_test_wholebody_test_9_D
)

# -------------------------------
# Copia de archivos
# -------------------------------
copiar_archivos() {
    origen=$1
    destino=$2

    archivos=(
        "Activity_distribution_data.txt"
        "Quantification_data.txt"
        "Quantification_data_whole_body.txt"
        "rec_OSEM3D_48.hdr"
        "rec_OSEM3D_48.img"
        "rec_OSEM3D_48_norm.hdr"
        "rec_OSEM3D_48_norm.img"
        "rec_OSEM3D_48_norm_wholeBody.hdr"
        "rec_OSEM3D_48_norm_wholeBody.img"
        "mask_image.nii"
    )

    for file in "${archivos[@]}"; do
        if [ -f "$origen/$file" ]; then
            cp "$origen/$file" "$destino/"
        else
            echo "⚠️ Archivo no encontrado: $file"
        fi
    done
}

# -------------------------------
# Crear info.txt
# -------------------------------
crear_info() {
    config=$1
    carpeta=$2
    origen=$3
    destino=$4

    fecha=$(date "+%Y-%m-%d %H:%M:%S")

    cat <<EOF > "$destino/info.txt"
Config: $config
Carpeta: $carpeta
Origen: $origen
Fecha de copia: $fecha
EOF
}

# -------------------------------
# Loop principal
# -------------------------------
total=${#configs[@]}
i=1

for config in "${configs[@]}"; do

    echo "----------------------------------------"
    echo "▶️ [$i/$total] Ejecutando: $config"

    # 1. Simulación
    python scripts/experiment_wholebody_claudia.py --config-name "$config"

    if [ $? -ne 0 ]; then
        echo "❌ Error en simulación: $config"
        exit 1
    fi

    # 2. Detectar A/B/C/D
    sufijo="${config##*_}"

    case $sufijo in
        A) carpeta="att_1_y_scatter_corr_0.15" ;;
        B) carpeta="att_0_y_scatter_corr_0.15" ;;
        C) carpeta="att_0_y_scatter_corr_0" ;;
        D) carpeta="att_0_y_scatter_corr_1" ;;
        *) echo "❌ Sufijo desconocido"; exit 1 ;;
    esac

    # 3. Origen datos
    if [[ $config == *"test_1"* ]]; then
        origen="/home/mibiolab/Data/Phantoms_Rata/PET_study_1_179.93uCi"
    elif [[ $config == *"test_9"* ]]; then
        origen="/home/mibiolab/Data/Phantoms_Rata/PET_study_9_175.61uCi"
    elif [[ $config == *"reference_eppendorff"* ]]; then
        origen="/home/mibiolab/Data/Phantoms_Rata/Eppendorff_101uCi_10min_12.02.26_test_1"
    else
        echo "❌ No se reconoce el tipo de config"
        exit 1
    fi

    # 4. Crear carpeta destino
    destino="./${config}/${carpeta}"
    mkdir -p "$destino"

    echo "📁 Carpeta creada: $destino"

    # 5. Copiar archivos
    echo "📂 Copiando archivos..."
    copiar_archivos "$origen" "$destino"

    # 6. Crear info.txt
    crear_info "$config" "$carpeta" "$origen" "$destino"

    echo "📝 info.txt creado"

    echo "✅ Completado: $config"

    ((i++))
done

echo "🎉 TODAS LAS SIMULACIONES TERMINADAS"
fi

echo "✅ Proceso de reconstrucción sin atenuación terminado"
