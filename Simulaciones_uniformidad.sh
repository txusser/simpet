# Simulaciones  NEC
#!/bin/bash

# Simulaciones Uniformidad del 1 al 49
for i in $(seq 1 49); do
    echo "🔄 Ejecutando config_test_Bruker_uniformidad_$i...😱 😱 😱 😱 😱 😱 😱 😱 😱 "
    
    # Dejar dos líneas en blanco antes de ejecutar python
    echo ""
    echo ""
    
    # Ejecutar el comando python con la configuración correspondiente
    python scripts/experiment.py --config-name config_test_Bruker_uniformidad_$i

    # Comprobar si el comando falló
    if [ $? -ne 0 ]; then
        echo "❌ Error al ejecutar config_test_$i. Deteniendo el script."
        exit 1
    fi
    
      # Dejar dos líneas en blanco antes de ejecutar python
    echo ""
    echo ""
    echo "🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩🤩"
    # Caritas de fiesta y confeti al terminar cada simulación
    echo "🎉🎊 Simulación config_test_Bruker_uniformidad_$i completada exitosamente! 🎊🎉"
    echo ""

done

# Al finalizar todas las simulaciones, mensaje de alegría
echo "🎉🎊 ¡Todas las simulaciones se completaron con éxito! 🎊🎉"
echo "😄🙌 ¡Gran trabajo! Todo ha terminado, ahora a celebrar el éxito de este esfuerzo. 🎉🎉 ¡Felicidades! 😄🙌"
echo "✅✅ ¡Todo listo para el siguiente paso! ✅✅"

