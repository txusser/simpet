#!/bin/bash

# Generar fichero config - Simulaciones NEC del 1 al 20
csv_file="coincidence_window.csv"

# Leer valores de la segunda columna, ignorando el encabezado
coincidence_window_values=($(tail -n +2 "$csv_file" | cut -d, -f2))

for i in $(seq 1 20); do
    coincidence_window="${coincidence_window_values[$((i-1))]}"
    
    nuevo_scanner_name="PET_MRI_scanner_Bruker_coincidence_windows_${coincidence_window}_WE50"
    nuevo_scanner_name_archivo="${nuevo_scanner_name}.yaml"

    echo "🔄 Generando $nuevo_scanner_name_archivo con coincidence_window: $coincidence_window..."

#    test -f Bruker_PET_MRI_scanner_Validado_modif_WE20 || { echo "❌ Archivo base no encontrado"; exit 1; }

    sed -e "s/\(coincidence_window:\s*\).*/\1$coincidence_window/" \
        -e "s/\(scanner_name:\s*\).*/\1\"$nuevo_scanner_name\"/" \
        Bruker_PET_MRI_scanner_Validado_modif_WE50.yaml > "$nuevo_scanner_name_archivo"
done

echo "✅ Archivos generados correctamente."

