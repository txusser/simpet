#Generar fichero config
# Simulaciones NEC del 1 al 45
#!/bin/bash

# Ruta al archivo CSV con los valores de 'Actividad en mCi'
csv_file="valores.csv"

# Leer los valores de "atividad en mCi" desde el CSV (suponiendo que está en la segunda columna)
total_dose_values=($(tail -n +2 "$csv_file" | cut -d, -f2))  # Tomar la segunda columna de los valores

for cama in 1 2; do
    for i in $(seq 1 19); do
        total_dose="${total_dose_values[$((i-1))]}" # El índice es i-1 
        nuevo_output_dir="Phantom_Rata_${i}_cama_${cama}"
        nombre_archivo="test_Rata_${i}_cama_${cama}.yaml"

        echo "🔄 Generando $nombre_archivo con total_dose: $total_dose y output_dir: $nuevo_output_dir..."

        archivo_base="test_phantom_rata_cama_${cama}.yaml"

        if [[ -f $archivo_base ]]; then
            sed -e "s/\(output_dir:\s*\).*/\1\"$nuevo_output_dir\"/" \
                -e "s/\(total_dose:\s*\).*/\1 $total_dose/" \
                "$archivo_base" > "$nombre_archivo"
        else
            echo "⚠️ Archivo $archivo_base no encontrado."
        fi
    done
done

echo "✅ Archivos generados correctamente con valores de output_dir y total_dose actualizados."

