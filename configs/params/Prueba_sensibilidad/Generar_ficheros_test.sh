#!/bin/bash

# Ruta al archivo CSV con los valores de 'Posición'
csv_file="Posición_center_slice.csv" 
        
# Leer los valores de "Posición_center_slice" desde el CSV (segunda columna, sin encabezado)
central_slice_values=($(tail -n +2 "$csv_file" | cut -d, -f2))

# Simulaciones del 1 al 31
for i in $(seq 1 31); do
    # Obtener el valor correspondiente
    central_slice="${central_slice_values[$((i-1))]}"
    pos_relativa=$(((central_slice - 301) / 4))

    # Calcular output_dir y nombre del archivo
    nuevo_output_dir="Prueba_sensibilidad_${central_slice}_posición_${pos_relativa}_WE20"
    nombre_archivo="test_sensibilidad_$i.yaml"

    echo "🔄 Generando $nombre_archivo con center_slice: $central_slice y output_dir: $nuevo_output_dir..."

    # Generar el archivo YAML con los valores actualizados
    sed -e "s/\(output_dir:\s*\).*/\1\"$nuevo_output_dir\"/" \
        -e "s/\(center_slice:\s*\).*/\1 $central_slice/" \
        test_claudia_Bruker_sensibilidad_validado.yaml > "$nombre_archivo"
done

echo "✅ Archivos generados correctamente con valores de output_dir y center_slice actualizados."

