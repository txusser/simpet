#Generar fichero config
# Simulaciones NEC del 1 al 20
#!/bin/bash

# Ruta al archivo CSV con los valores de 'coincidence_window'
csv_file="coincidence_window.csv"

# Leer los valores de "coincidence window en ns" desde el CSV (suponiendo que está en la segunda columna)
coincidence_window_values=($(tail -n +2 "$csv_file" | cut -d, -f2))  # Tomar la segunda columna de los valores

# Simulaciones NEC del 1 al 20
for i in $(seq 1 20); do

    # Obtener el valor correspondiente de 'coincidence_window' desde el CSV
    coincidence_window="${coincidence_window_values[$((i-1))]}"  # El índice es i-1 porque el array empieza en 0

    # Calcular el valor para scanner
    nuevo_scanner_name="PET_MRI_scanner_Bruker_coincidence_windows_${coincidence_window}_WE50"

    # Calcular el valor para output_dir
    nuevo_output_dir="Prueba_NECR_${coincidence_window}ns_WE50_0.069mCi"  

    # Nombre del archivo a generar
    nombre_archivo="test_curva_NECR_coincidence_window_${i}_WE50.yaml"

    echo "🔄 Generando $nombre_archivo con coincidence_window: $coincidence_window y output_dir: $nuevo_output_dir..."

    # Reemplazar los valores en el archivo YAML
    sed -e "s/\(output_dir:\s*\).*/\1\"$nuevo_output_dir\"/" \
        -e "s/\(        - scanner:\s*\).*/\1$nuevo_scanner_name/" \
        test_claudia_Bruker_NEC.yaml > "$nombre_archivo"
done

echo "✅ Archivos generados correctamente con valores de output_dir y total_dose actualizados."



