"""Acceso a las placas PCA9685 por I2C (una o dos)."""
import board
import busio
from adafruit_pca9685 import PCA9685

from config import (
    PCA_ADDR_1, PCA_ADDR_2, PWM_FREQ,
    SERVO_MIN_US, SERVO_MAX_US, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE,
    resolve_channel,
)


class PCAManager:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca_a = PCA9685(self.i2c, address=PCA_ADDR_1)
        self.pca_a.frequency = PWM_FREQ
        self.pca_b = None
        if PCA_ADDR_2 is not None:
            try:
                self.pca_b = PCA9685(self.i2c, address=PCA_ADDR_2)
                self.pca_b.frequency = PWM_FREQ
            except (ValueError, OSError):
                print(f"AVISO: no encontre la segunda placa en {hex(PCA_ADDR_2)}")
        self._avisados = set()

    def set_angle_logical(self, logical_channel, angle):
        board_id, ch = resolve_channel(logical_channel)
        pca = self.pca_a if board_id == "A" else self.pca_b
        if pca is None:
            if logical_channel not in self._avisados:
                self._avisados.add(logical_channel)
                print(f"AVISO: canal {logical_channel} sin placa, se ignora")
            return
        angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, angle))
        span = SERVO_MAX_ANGLE - SERVO_MIN_ANGLE
        pulse = SERVO_MIN_US + (angle - SERVO_MIN_ANGLE) / span * (SERVO_MAX_US - SERVO_MIN_US)
        pca.channels[ch].duty_cycle = int(pulse / (1_000_000 / PWM_FREQ) * 0xFFFF)

    def release_all(self):
        """Quita la senal PWM de todos los canales (los servos quedan sin fuerza)."""
        for pca in (self.pca_a, self.pca_b):
            if pca is None:
                continue
            for ch in range(16):
                pca.channels[ch].duty_cycle = 0
            pca.deinit()
