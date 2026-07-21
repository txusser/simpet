#Generar fichero config
# Simulaciones NEC del 1 al 45
#!/bin/bash
#!/bin/bash

for i in $(seq 1 49); do
    nuevo_param="test_claudia_Bruker_uniformidad_$i"
    nombre_archivo="config_test_Bruker_uniformidad_$i.yaml"

    echo "🔄 Generando $nombre_archivo con params: $nuevo_param..."

    # Reemplaza solo el valor después de ":"
    sed "s/\(- params:\s*\).*/\1$nuevo_param/" \
        config_test_Bruker_Prueba_uniformidad.yaml > "$nombre_archivo"
done

echo "✅ Archivos generados correctamente con valores de params actualizados."

