"""Marchas del hexapodo (tripode), giros y posturas.

Todos los angulos de la marcha son RELATIVOS al neutral calibrado de cada
servo (config.SERVO_CALIBRATION), asi cada pata baja a su propia posicion de
reposo y no a un 90 generico.

El movimiento esta sincronizado: todas las articulaciones de un mismo
movimiento salen y llegan a la vez, con arranque y frenado suaves.
"""
import time

from config import SERVO_CALIBRATION

TRIPOD_A = ["L1", "L3", "R2"]
TRIPOD_B = ["L2", "R1", "R3"]

# Cuanto se mueve cada articulacion respecto a su neutral (grados).
COXA_SWING = 20          # avance / retroceso de la coxa
FEMUR_LIFT_DELTA = -30   # el femur sube al levantar la pata
TIBIA_LIFT_DELTA = 40    # la tibia sube al levantar la pata

# Velocidad: valores altos de MICRO_DELAY = movimiento mas lento.
# Con INCREMENT=1 y MICRO_DELAY=0.06 una articulacion de 40 grados tarda ~2.4 s.
DEFAULT_INCREMENT = 1
DEFAULT_MICRO_DELAY = 0.06
DEFAULT_GROUP_DELAY = 0.5
DEFAULT_PAUSE = 0.8


def _n(name, joint):
    return SERVO_CALIBRATION[(name, joint)]["neutral"]


def move_joints_smooth(moves, increment=DEFAULT_INCREMENT, micro_delay=DEFAULT_MICRO_DELAY):
    """Mueve varias articulaciones a la vez.

    `moves` es una lista de tuplas (leg, joint, target_angle). Todas salen y
    llegan juntas: cada una avanza proporcional a su recorrido, con un perfil
    suave (smoothstep). El objetivo se recorta a [min, max] de la calibracion.
    """
    plan = []
    for leg, joint, target in moves:
        cal = SERVO_CALIBRATION[(leg.name, joint)]
        target = max(cal["min"], min(cal["max"], target))
        plan.append((leg, joint, leg.current_angles[joint], target))

    max_dist = max((abs(t - s) for _, _, s, t in plan), default=0)
    if max_dist == 0:
        return

    n = max(1, int(round(max_dist / increment)))
    for i in range(1, n + 1):
        f = i / n
        f = f * f * (3 - 2 * f)  # arranque y frenado suaves
        for leg, joint, start, target in plan:
            leg.set_joint(joint, int(round(start + (target - start) * f)))
        time.sleep(micro_delay)


def lift_leg(legs, leg_names, increment=DEFAULT_INCREMENT, micro_delay=DEFAULT_MICRO_DELAY):
    moves = []
    for name in leg_names:
        leg = legs[name]
        moves.append((leg, "femur", _n(name, "femur") + FEMUR_LIFT_DELTA))
        moves.append((leg, "tibia", _n(name, "tibia") + TIBIA_LIFT_DELTA))
    move_joints_smooth(moves, increment, micro_delay)


def lower_leg(legs, leg_names, increment=DEFAULT_INCREMENT, micro_delay=DEFAULT_MICRO_DELAY):
    moves = []
    for name in leg_names:
        leg = legs[name]
        moves.append((leg, "femur", _n(name, "femur")))
        moves.append((leg, "tibia", _n(name, "tibia")))
    move_joints_smooth(moves, increment, micro_delay)


def swing_coxa(legs, coxa_targets, increment=DEFAULT_INCREMENT, micro_delay=DEFAULT_MICRO_DELAY):
    """coxa_targets: dict nombre_de_pata -> angulo objetivo de coxa."""
    moves = [(legs[name], "coxa", angle) for name, angle in coxa_targets.items()]
    move_joints_smooth(moves, increment, micro_delay)


def _step_cycle(legs, swing_group, stance_group, coxa_targets,
                increment=DEFAULT_INCREMENT, micro_delay=DEFAULT_MICRO_DELAY):
    """Medio ciclo tripode: levanta swing_group, mueve las coxas de ambos
    grupos (el grupo de apoyo empuja el cuerpo) y apoya swing_group."""
    lift_leg(legs, swing_group, increment, micro_delay)
    swing_coxa(legs, coxa_targets, increment, micro_delay)
    lower_leg(legs, swing_group, increment, micro_delay)


def _forward_targets(swing_group, stance_group):
    t = {n: _n(n, "coxa") + COXA_SWING for n in swing_group}
    t.update({n: _n(n, "coxa") - COXA_SWING for n in stance_group})
    return t


def _backward_targets(swing_group, stance_group):
    t = {n: _n(n, "coxa") - COXA_SWING for n in swing_group}
    t.update({n: _n(n, "coxa") + COXA_SWING for n in stance_group})
    return t


def _turn_targets(swing_group, stance_group, direction):
    """Para girar en el sitio, el lado izquierdo y el derecho 'caminan' en
    sentidos opuestos. La inversion de las patas R ya la resuelve
    Leg._apply_calibration, esto solo decide el sentido de la marcha por lado."""
    def walks_forward(name):
        return name.startswith("L") == (direction == "right")

    def target_for(name, is_swing):
        sign = 1 if (walks_forward(name) == is_swing) else -1
        return _n(name, "coxa") + sign * COXA_SWING

    t = {n: target_for(n, True) for n in swing_group}
    t.update({n: target_for(n, False) for n in stance_group})
    return t


def _walk_stride(legs, target_fn, increment, micro_delay, pause):
    _step_cycle(legs, TRIPOD_A, TRIPOD_B, target_fn(TRIPOD_A, TRIPOD_B), increment, micro_delay)
    time.sleep(pause)
    _step_cycle(legs, TRIPOD_B, TRIPOD_A, target_fn(TRIPOD_B, TRIPOD_A), increment, micro_delay)
    time.sleep(pause)


def walk_forward(legs, steps=5, increment=DEFAULT_INCREMENT,
                 micro_delay=DEFAULT_MICRO_DELAY, pause=DEFAULT_PAUSE):
    for i in range(steps):
        print(f"Paso adelante {i + 1}/{steps}")
        _walk_stride(legs, _forward_targets, increment, micro_delay, pause)


def walk_backward(legs, steps=5, increment=DEFAULT_INCREMENT,
                  micro_delay=DEFAULT_MICRO_DELAY, pause=DEFAULT_PAUSE):
    for i in range(steps):
        print(f"Paso atras {i + 1}/{steps}")
        _walk_stride(legs, _backward_targets, increment, micro_delay, pause)


def _turn(legs, direction, steps, increment, micro_delay, pause):
    for i in range(steps):
        print(f"Giro {direction} {i + 1}/{steps}")
        _step_cycle(legs, TRIPOD_A, TRIPOD_B,
                    _turn_targets(TRIPOD_A, TRIPOD_B, direction), increment, micro_delay)
        time.sleep(pause)
        _step_cycle(legs, TRIPOD_B, TRIPOD_A,
                    _turn_targets(TRIPOD_B, TRIPOD_A, direction), increment, micro_delay)
        time.sleep(pause)


def turn_left(legs, steps=5, increment=DEFAULT_INCREMENT,
              micro_delay=DEFAULT_MICRO_DELAY, pause=DEFAULT_PAUSE):
    _turn(legs, "left", steps, increment, micro_delay, pause)


def turn_right(legs, steps=5, increment=DEFAULT_INCREMENT,
               micro_delay=DEFAULT_MICRO_DELAY, pause=DEFAULT_PAUSE):
    _turn(legs, "right", steps, increment, micro_delay, pause)


def set_body_height(legs, height_delta=0, increment=DEFAULT_INCREMENT,
                    micro_delay=DEFAULT_MICRO_DELAY, group_delay=DEFAULT_GROUP_DELAY):
    """Sube (delta > 0) o baja (delta < 0) el cuerpo ajustando femur y tibia
    de las 6 patas respecto a su neutral. Usar valores pequenos. Los dos
    tripodes se mueven con desfase para repartir el pico de corriente."""
    for group in (TRIPOD_A, TRIPOD_B):
        moves = []
        for name in group:
            leg = legs[name]
            moves.append((leg, "femur", _n(name, "femur") - height_delta))
            moves.append((leg, "tibia", _n(name, "tibia") - height_delta))
        move_joints_smooth(moves, increment, micro_delay)
        time.sleep(group_delay)


def stand_neutral(legs, increment=DEFAULT_INCREMENT,
                  micro_delay=DEFAULT_MICRO_DELAY, group_delay=DEFAULT_GROUP_DELAY):
    """Lleva todas las patas a su neutral calibrado, un tripode a la vez.

    Primero reenvia el angulo actual de cada servo: al arrancar el programa
    Leg.current_angles ya vale el neutral, asi que sin este paso no se
    mandaria ninguna senal PWM y los servos no tomarian la postura.
    """
    for group in (TRIPOD_A, TRIPOD_B):
        moves = []
        for name in group:
            leg = legs[name]
            for joint in ("coxa", "femur", "tibia"):
                leg.set_joint(joint, leg.current_angles[joint])
                moves.append((leg, joint, _n(name, joint)))
        move_joints_smooth(moves, increment, micro_delay)
        time.sleep(group_delay)
