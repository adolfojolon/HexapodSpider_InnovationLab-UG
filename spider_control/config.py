"""Configuracion del hexapodo: placas I2C, canales por pata y calibracion.

Los angulos de reposo (neutral) NO se escriben aqui: se leen de
calibracion_servos.json, en la carpeta raiz del proyecto (la que contiene
spider_control/ y tools/), el archivo que genera tools/calibrar_servos.py.
Se puede cambiar la ruta con la variable de entorno SPIDER_CALIBRATION.
"""
import json
import os

# --- Placas PCA9685 ---
PCA_ADDR_1 = 0x42   # placa 1 (jumper A1 soldado): patas IZQUIERDAS L1-L3
PCA_ADDR_2 = 0x40   # placa 2 (sin jumpers):          patas DERECHAS  R1-R3
                    # Evita 0x70 (all-call del PCA9685).

PWM_FREQ = 50

SERVO_MIN_US = 500
SERVO_MAX_US = 2500
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180

LEG_NAMES = ["L1", "L2", "L3", "R1", "R2", "R3"]


def resolve_channel(logical_channel):
    """Canal logico -> (placa, canal fisico 0-15).

    Logico 0-15 = placa 1 (0x42). Logico 16-31 = placa 2 (0x40), o sea el
    canal fisico 0 de la placa 2 es el logico 16."""
    if logical_channel < 16:
        return ("A", logical_channel)
    return ("B", logical_channel - 16)


# Orden fisico por pata: tibia, femur, coxa.
# Placa 1 (0x42), canales 0-8:  patas izquierdas.
# Placa 2 (0x40), canales 0-8:  patas derechas (logicos 16-24).
LEG_CHANNELS = {
    "L1": {"tibia": 0,  "femur": 1,  "coxa": 2},
    "L2": {"tibia": 3,  "femur": 4,  "coxa": 5},
    "L3": {"tibia": 6,  "femur": 7,  "coxa": 8},
    "R1": {"tibia": 16, "femur": 17, "coxa": 18},
    "R2": {"tibia": 19, "femur": 20, "coxa": 21},
    "R3": {"tibia": 22, "femur": 23, "coxa": 24},
}

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIBRATION_FILE = os.environ.get(
    "SPIDER_CALIBRATION", os.path.join(PROJECT_ROOT, "calibracion_servos.json")
)


def _load_calibration():
    try:
        with open(CALIBRATION_FILE) as f:
            saved = json.load(f)
    except (OSError, ValueError) as e:
        print(f"AVISO: no pude leer {CALIBRATION_FILE} ({e}); uso 90 en todo")
        saved = {}

    cal = {}
    for leg in LEG_NAMES:
        inv = leg.startswith("R")
        for joint in ("coxa", "femur", "tibia"):
            ch = LEG_CHANNELS[leg][joint]
            key = f"h:{ch}" if ch < 16 else f"h2:{ch - 16}"
            if key in saved:
                phys = saved[key]
            else:
                phys = 90
                print(f"AVISO: sin calibracion para {leg} {joint} ({key}), uso 90")
            # El JSON guarda el angulo fisico que recibe el servo. En las patas
            # derechas Leg._apply_calibration invierte (180 - angulo), asi que
            # el neutral "logico" es 180 - fisico.
            neutral = 180 - phys if inv else phys
            cal[(leg, joint)] = {
                "neutral": neutral, "min": 0, "max": 180, "invert": inv,
            }
    return cal


SERVO_CALIBRATION = _load_calibration()
