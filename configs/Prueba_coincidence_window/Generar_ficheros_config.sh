#Generar fichero config
# Simulaciones NEC del 1 al 45
#!/bin/bash
#!/bin/bash

for i in $(seq 1 20); do
    nuevo_param="test_curva_NECR_coincidence_window_${i}_WE50"
    nombre_archivo="config_test_curva_NECR_coincidence_window_${i}_WE50.yaml"

    echo "🔄 Generando $nombre_archivo con params: $nuevo_param..."

    # Reemplaza solo el valor después de ":"
    sed "s/\(- params:\s*\).*/\1$nuevo_param/" \
        config_test_Bruker_NEC_disco_externo.yaml > "$nombre_archivo"
done

echo "✅ Archivos generados correctamente con valores de params actualizados."

