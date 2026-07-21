import os
import shutil
import sys

origen = "/media/claudia/Seagate Basic/uniformidad F18 correc 20%"
destino = "/home/mibiolab/Data/Uniformidad_claudia"

# -------------------------------
# Calcular tamaño total carpeta
# -------------------------------
def tamaño_carpeta(ruta):
    total = 0
    for root, dirs, files in os.walk(ruta):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

# -------------------------------
# Barra de progreso
# -------------------------------
def barra_progreso(porcentaje, longitud=30):
    llenos = int(longitud * porcentaje // 100)
    vacios = longitud - llenos
    return "█" * llenos + "░" * vacios

# -------------------------------
# Copiar con progreso
# -------------------------------
def copiar_con_progreso(carpeta_origen, carpeta_destino, nombre_carpeta, idx, total_carpetas):
    total_bytes = tamaño_carpeta(carpeta_origen)
    copiados = 0

    if total_bytes == 0:
        print(f"\n📁 [{idx}/{total_carpetas}] {nombre_carpeta} vacía ✔")
        return

    for root, dirs, files in os.walk(carpeta_origen):
        ruta_relativa = os.path.relpath(root, carpeta_origen)
        destino_actual = os.path.join(carpeta_destino, ruta_relativa)

        os.makedirs(destino_actual, exist_ok=True)

        for f in files:
            origen_f = os.path.join(root, f)
            destino_f = os.path.join(destino_actual, f)

            shutil.copy2(origen_f, destino_f)
            copiados += os.path.getsize(origen_f)

            porcentaje = (copiados / total_bytes) * 100
            barra = barra_progreso(porcentaje)

            sys.stdout.write(
                f"\r📁 [{idx}/{total_carpetas}] {nombre_carpeta} |{barra}| {porcentaje:6.2f}%"
            )
            sys.stdout.flush()

    print(" ✔")

# -------------------------------
# Programa principal
# -------------------------------
def main():
    if not os.path.exists(destino):
        os.makedirs(destino)

    carpetas = [c for c in os.listdir(origen) if os.path.isdir(os.path.join(origen, c))]
    total_carpetas = len(carpetas)

    print(f"\n🚀 Iniciando copia de {total_carpetas} carpetas...\n")

    for i, carpeta in enumerate(carpetas, start=1):
        ruta_carpeta = os.path.join(origen, carpeta)
        destino_carpeta = os.path.join(destino, carpeta)

        copiar_con_progreso(
            ruta_carpeta,
            destino_carpeta,
            carpeta,
            i,
            total_carpetas
        )

    print("\n✅ Todas las carpetas copiadas correctamente\n")

# -------------------------------
if __name__ == "__main__":
    main()
