"""Control interactivo por consola (sin entorno grafico).

Escribe un comando y Enter. Opcionalmente un numero de pasos: "w 3".

    w  caminar adelante      s  caminar atras
    a  girar a la izquierda  d  girar a la derecha
    n  posicion neutral      +  subir cuerpo      -  bajar cuerpo
    p  mostrar angulos actuales de cada servo
    q  salir (suelta los servos)

Ctrl+C detiene el movimiento y vuelve al prompt sin salir.
"""
import time

from pca_manager import PCAManager
from leg import Leg
from config import LEG_NAMES
import gaits

AYUDA = __doc__.split("\n\n", 1)[1]


def mostrar_angulos(legs):
    print(f"{'Pata':4} {'coxa':>5} {'femur':>6} {'tibia':>6}   (angulos logicos actuales)")
    for name in LEG_NAMES:
        a = legs[name].current_angles
        print(f"{name:4} {a['coxa']:5} {a['femur']:6} {a['tibia']:6}")


def main():
    pca = PCAManager()
    legs = {name: Leg(pca, name) for name in LEG_NAMES}
    altura = 0
    try:
        print("Poniendo la arana en posicion neutra...")
        gaits.stand_neutral(legs)
        print(AYUDA)
        while True:
            try:
                partes = input("\n>> ").strip().lower().split()
                if not partes:
                    continue
                cmd = partes[0]
                pasos = int(partes[1]) if len(partes) > 1 else 1
                if cmd == "q":
                    break
                elif cmd == "w":
                    gaits.walk_forward(legs, steps=pasos)
                elif cmd == "s":
                    gaits.walk_backward(legs, steps=pasos)
                elif cmd == "a":
                    gaits.turn_left(legs, steps=pasos)
                elif cmd == "d":
                    gaits.turn_right(legs, steps=pasos)
                elif cmd == "n":
                    altura = 0
                    gaits.stand_neutral(legs)
                elif cmd in ("+", "-"):
                    altura += 3 if cmd == "+" else -3
                    print(f"Altura del cuerpo: {altura:+d} grados respecto al neutral")
                    gaits.set_body_height(legs, altura)
                elif cmd == "p":
                    mostrar_angulos(legs)
                else:
                    print("Comando no valido.\n" + AYUDA)
            except ValueError:
                print("Escribe el comando y, si quieres, un numero de pasos: w 3")
            except KeyboardInterrupt:
                print("\nMovimiento detenido. Escribe 'n' para volver al neutral o 'q' para salir.")
    finally:
        pca.release_all()
        print("Servos liberados.")


if __name__ == "__main__":
    main()
