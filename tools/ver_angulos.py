"""Muestra los angulos que usa el robot, sin tocar el hardware.

Para cada servo: placa y canal, neutral guardado, angulo FISICO que recibe
el servo (en las patas R se invierte: 180 - angulo) y los angulos al
levantar la pata y al avanzar/retroceder la coxa.

Uso (desde la carpeta del proyecto):
    python3 tools/ver_angulos.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spider_control"))

import config
import gaits
from config import LEG_NAMES, LEG_CHANNELS, SERVO_CALIBRATION, resolve_channel


def fisico(leg, joint, logico):
    cal = SERVO_CALIBRATION[(leg, joint)]
    a = max(cal["min"], min(cal["max"], logico))
    return 180 - a if cal["invert"] else a


def main():
    print(f"Archivo de calibracion: {config.CALIBRATION_FILE}")
    print(f"Placa 1 = {hex(config.PCA_ADDR_1)} | Placa 2 = {hex(config.PCA_ADDR_2) if config.PCA_ADDR_2 else 'sin placa'}")
    print(f"COXA_SWING={gaits.COXA_SWING}  FEMUR_LIFT_DELTA={gaits.FEMUR_LIFT_DELTA}  TIBIA_LIFT_DELTA={gaits.TIBIA_LIFT_DELTA}")
    print(f"Velocidad: incremento={gaits.DEFAULT_INCREMENT} grado, micro_delay={gaits.DEFAULT_MICRO_DELAY} s\n")
    print("Los angulos 'fisicos' son los que realmente recibe cada servo.\n")
    cab = f"{'Pata':4} {'Art.':6} {'Placa':5} {'Can':3} | {'neutral':>7} {'FISICO':>6} | {'levantada':>9} {'FISICO':>6} | {'avanza':>6} {'FISICO':>6} {'atras':>5} {'FISICO':>6}"
    print(cab)
    print("-" * len(cab))
    for leg in LEG_NAMES:
        for joint in ("coxa", "femur", "tibia"):
            ch = LEG_CHANNELS[leg][joint]
            placa, fis = resolve_channel(ch)
            n = SERVO_CALIBRATION[(leg, joint)]["neutral"]
            if joint == "coxa":
                lev = lev_f = ""
                av, at = n + gaits.COXA_SWING, n - gaits.COXA_SWING
                av_f, at_f = fisico(leg, joint, av), fisico(leg, joint, at)
            else:
                d = gaits.FEMUR_LIFT_DELTA if joint == "femur" else gaits.TIBIA_LIFT_DELTA
                lev = n + d
                lev_f = fisico(leg, joint, lev)
                av = at = av_f = at_f = ""
            print(f"{leg:4} {joint:6} {placa:5} {fis:3} | {n:7} {fisico(leg, joint, n):6} | {lev!s:>9} {lev_f!s:>6} | {av!s:>6} {av_f!s:>6} {at!s:>5} {at_f!s:>6}")
    print("\nNota: avanza/atras son para las patas del grupo que se mueve hacia adelante;")
    print("en la marcha, un tripode usa 'avanza' mientras el otro usa 'atras' (y se alternan).")


if __name__ == "__main__":
    main()
