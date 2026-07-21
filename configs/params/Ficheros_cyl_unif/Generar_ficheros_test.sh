#Generar fichero config
# Simulaciones NEC del 1 al 38
#!/bin/bash

# Ruta al archivo CSV con los valores de 'Actividad en mCi'
csv_file="valores_actividad_uniformidad.csv"

# Leer los valores de "Actividad en mCi" desde el CSV (suponiendo que está en la segunda columna)
total_dose_values=($(tail -n +2 "$csv_file" | cut -d, -f2))  # Tomar la segunda columna de los valores

# Simulaciones NEC del 1 al 45
for i in $(seq 1 49); do
    # Obtener el valor correspondiente de 'total_dose' desde el CSV
    total_dose="${total_dose_values[$((i-1))]}"  # El índice es i-1 porque el array empieza en 0

    # Calcular el valor para output_dir
    nuevo_output_dir="Prueba_cyl_uniformidad_${total_dose}mCi_5min_F18_WE20"  

    # Nombre del archivo a generar
    nombre_archivo="test_claudia_Bruker_uniformidad_$i.yaml"

    echo "🔄 Generando $nombre_archivo con total_dose: $total_dose y output_dir: $nuevo_output_dir..."

    # Reemplazar los valores en el archivo YAML
    sed -e "s/\(output_dir:\s*\).*/\1\"$nuevo_output_dir\"/" \
        -e "s/\(total_dose:\s*\).*/\1 $total_dose/" \
        test_claudia_Bruker_Prueba_uniformidad.yaml > "$nombre_archivo"
done

echo "✅ Archivos generados correctamente con valores de output_dir y total_dose actualizados."



