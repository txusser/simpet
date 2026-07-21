#Generar fichero config
# Simulaciones NEC del 1 al 31
#!/bin/bash
#!/bin/bash

for i in $(seq 1 31); do
    nuevo_param="test_sensibilidad_$i"
    nombre_archivo="config_test_sensibilidad_$i.yaml"

    echo "🔄 Generando $nombre_archivo con params: $nuevo_param..."

    # Reemplaza solo el valor después de ":"
    sed "s/\(- params:\s*\).*/\1$nuevo_param/" \
        config_test_Bruker_sensibilidad_validado.yaml > "$nombre_archivo"
done

echo "✅ Archivos generados correctamente con valores de params actualizados."

