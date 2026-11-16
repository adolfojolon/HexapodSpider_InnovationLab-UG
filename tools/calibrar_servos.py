"""Calibracion interactiva de servos por consola (sin entorno grafico).

Mueve un servo a la vez y guarda el angulo de reposo en
~/calibracion_servos.json, el archivo que lee spider_control/config.py.

Uso:
    python3 calibrar_servos.py            # canales 0-15 (HAT, 0x42)
    python3 calibrar_servos.py 0x40       # ademas, canales 16-17 en una 2a placa

Claves guardadas: "h:<canal>" para la placa 0x42 y "h2:<canal>" para la segunda.
"""
import json
import os
import sys

import board
import busio
from adafruit_pca9685 import PCA9685

ARCHIVO = os.environ.get(
    "SPIDER_CALIBRATION", os.path.expanduser("~/calibracion_servos.json")
)
HAT_ADDR = 0x42

# Etiqueta de cada canal logico: 3 servos por pata en el orden tibia, femur, coxa.
ETIQUETAS = {}
for i, pata in enumerate(["L1", "L2", "L3", "R1", "R2", "R3"]):
    for j, art in enumerate(["tibia", "femur", "coxa"]):
        ETIQUETAS[i * 3 + j] = f"{pata} {art}"

i2c = busio.I2C(board.SCL, board.SDA)
pca_a = PCA9685(i2c, address=HAT_ADDR)
pca_a.frequency = 50

pca_b = None
if len(sys.argv) > 1:
    pca_b = PCA9685(i2c, address=int(sys.argv[1], 0))
    pca_b.frequency = 50


def placa_y_clave(canal):
    """Canal logico -> (placa, canal fisico, clave del JSON) o None si no existe."""
    if canal < 16:
        return pca_a, canal, f"h:{canal}"
    if pca_b is None:
        return None
    return pca_b, canal - 16, f"h2:{canal - 16}"


def mover(pca, canal_fisico, angulo):
    angulo = max(0, min(180, angulo))
    us = 500 + angulo / 180.0 * 2000
    pca.channels[canal_fisico].duty_cycle = int(us / 20000.0 * 0xFFFF)


def cargar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO) as f:
            return json.load(f)
    return {}


def guardar(datos):
    with open(ARCHIVO, "w") as f:
        json.dump(datos, f, indent=2)


def calibrar(canal, datos):
    pca, fisico, clave = placa_y_clave(canal)
    angulo = datos.get(clave, 90)
    print(f"\n--- Canal {canal} ({ETIQUETAS.get(canal, '?')}) ---")
    print("numero 0-180 = mover | g = guardar | o = apagar | s = saltar | q = salir")
    mover(pca, fisico, angulo)
    print(f"Angulo actual: {angulo}")
    while True:
        e = input(">> ").strip().lower()
        if e == "q":
            return "salir"
        if e == "s":
            return "saltar"
        if e == "o":
            pca.channels[fisico].duty_cycle = 0
            print("Canal apagado.")
        elif e == "g":
            datos[clave] = angulo
            guardar(datos)
            print(f"Guardado {clave} = {angulo}")
            return "ok"
        else:
            try:
                angulo = max(0, min(180, int(e)))
                mover(pca, fisico, angulo)
                print(f"Angulo actual: {angulo}")
            except ValueError:
                print("Entrada no valida.")


def main():
    datos = cargar()
    maximo = 17 if pca_b else 15
    print(f"Archivo: {ARCHIVO}")
    print(f"Guardados: {datos}\n")
    while True:
        e = input(f"Canal (0-{maximo}, q = salir): ").strip().lower()
        if e == "q":
            break
        try:
            canal = int(e)
            if not 0 <= canal <= maximo:
                raise ValueError
        except ValueError:
            print("Canal invalido.")
            continue
        if calibrar(canal, datos) == "salir":
            break
    pca_a.deinit()
    if pca_b:
        pca_b.deinit()


if __name__ == "__main__":
    main()
