# Simulaciones  NEC
#!/bin/bash

# Simulaciones NEC del 1 al 45
for i in $(seq 42 45); do        # 3 5 7 10 15 26; do    #$(seq 1 45); do
    echo "🔄 Ejecutando config_test_curva_NECR_${i}_WE20...😱 😱 😱 😱 😱 😱 😱 😱 😱 "
    
    # Dejar dos líneas en blanco antes de ejecutar python
    echo ""
    echo ""
    
    # Ejecutar el comando python con la configuración correspondiente
    python scripts/experiment.py --config-name config_test_curva_NECR_${i}_WE20

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
    echo "🎉🎊 Simulación config_test_curva_NECR_${i}_WE20 completada exitosamente! 🎊🎉"
    echo ""

done

# Al finalizar todas las simulaciones, mensaje de alegría
echo "🎉🎊 ¡Todas las simulaciones se completaron con éxito! 🎊🎉"
echo "😄🙌 ¡Gran trabajo! Todo ha terminado, ahora a celebrar el éxito de este esfuerzo. 🎉🎉 ¡Felicidades! 😄🙌"
echo "✅✅ ¡Todo listo para el siguiente paso! ✅✅"

