"""Calibracion interactiva de servos por consola (sin entorno grafico).

Mueve un servo a la vez y guarda el angulo de reposo en
calibracion_servos.json, en la raiz del proyecto (junto a spider_control/ y
tools/), el archivo que lee spider_control/config.py.

Uso:
    python3 calibrar_servos.py            # placa 1 (0x42) y placa 2 (0x40)
    python3 calibrar_servos.py 0x41       # otra direccion para la placa 2

Canales que se piden (logicos):
    0-8    patas izquierdas L1-L3  (placa 1, 0x42)
    16-24  patas derechas  R1-R3   (placa 2, 0x40; fisicos 0-8 de esa placa)

Claves guardadas: "h:<canal>" para la placa 1 y "h2:<canal fisico>" para la 2.
"""
import json
import os
import sys

import board
import busio
from adafruit_pca9685 import PCA9685

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = os.environ.get(
    "SPIDER_CALIBRATION", os.path.join(RAIZ, "calibracion_servos.json")
)
HAT_ADDR = 0x42

# Etiqueta de cada canal logico: 3 servos por pata en el orden tibia, femur, coxa.
ETIQUETAS = {}
for i, pata in enumerate(["L1", "L2", "L3"]):
    for j, art in enumerate(["tibia", "femur", "coxa"]):
        ETIQUETAS[i * 3 + j] = f"{pata} {art}"
for i, pata in enumerate(["R1", "R2", "R3"]):
    for j, art in enumerate(["tibia", "femur", "coxa"]):
        ETIQUETAS[16 + i * 3 + j] = f"{pata} {art}"
CANALES_VALIDOS = sorted(ETIQUETAS)

i2c = busio.I2C(board.SCL, board.SDA)
pca_a = PCA9685(i2c, address=HAT_ADDR)
pca_a.frequency = 50

HAT2_ADDR = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x40
pca_b = None
try:
    pca_b = PCA9685(i2c, address=HAT2_ADDR)
    pca_b.frequency = 50
except (ValueError, OSError):
    print(f"AVISO: no encontre la placa 2 en {hex(HAT2_ADDR)}; solo patas izquierdas")


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
    validos = [c for c in CANALES_VALIDOS if c < 16 or pca_b]
    print(f"Archivo: {ARCHIVO}")
    print(f"Guardados: {datos}\n")
    while True:
        e = input("Canal (0-8 izquierdas, 16-24 derechas, q = salir): ").strip().lower()
        if e == "q":
            break
        try:
            canal = int(e)
            if canal not in validos:
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
