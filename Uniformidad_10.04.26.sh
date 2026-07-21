#!/bin/bash

echo "=============================="
echo "Iniciando copia..."
echo "=============================="

python3 copiar_simulaciones_uniformidad.py

if [ $? -ne 0 ]; then
    echo "❌ Error en la copia. Abortando."
    exit 1
fi

echo "✅ Copia terminada"

echo "=============================="
echo "Iniciando reconstrucciones..."
echo "=============================="

./Simulaciones_uniformidad.sh

if [ $? -ne 0 ]; then
    echo "❌ Error en las reconstrucciones."
    exit 1
fi

echo "✅ Proceso de reconstrucción sin atenuación terminado"
