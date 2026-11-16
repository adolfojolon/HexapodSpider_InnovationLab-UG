import time

from pca_manager import PCAManager
from leg import Leg
from config import LEG_NAMES
from gaits import walk_forward, stand_neutral


def build_legs(pca):
    return {name: Leg(pca, name) for name in LEG_NAMES}


def main():
    pca = PCAManager()
    legs = build_legs(pca)

    try:
        print("Poniendo la arana en posicion neutra...")
        stand_neutral(legs)
        time.sleep(1)

        print("Iniciando caminata hacia adelante...")
        walk_forward(legs, steps=2)  # sube 'steps' cuando la marcha ya sea estable

        print("Volviendo a posicion neutra...")
        stand_neutral(legs)

    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        pca.release_all()
        print("Servos liberados.")


if __name__ == "__main__":
    main()
