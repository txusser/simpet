#Generar fichero config
# Ratas de 2 cama
#!/bin/bash
#!/bin/bash
for cama in 1 2; do
    for i in $(seq 1 19); do
        nuevo_param="test_Rata_${i}_cama_${cama}"
        nombre_archivo="config_test_phantom_Rata_${i}_cama_${cama}.yaml"
        archivo_base="config_test_phantom_rata_cama_${cama}.yaml"

        echo "🔄 Generando $nombre_archivo con params: $nuevo_param..."

        if [[ -f "$archivo_base" ]]; then
            sed -E "s/(- params:[[:space:]]*).*/\1 test_Rata_${i}_cama_${cama}/" "$archivo_base" > "$nombre_archivo"
        else
            echo "⚠️ Archivo base $archivo_base no encontrado."
        fi
    done
done

echo "✅ Archivos generados correctamente con valores de params actualizados."

