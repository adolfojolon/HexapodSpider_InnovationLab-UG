"""Una pata del hexapodo: coxa, femur y tibia."""
from config import LEG_CHANNELS, SERVO_CALIBRATION


class Leg:
    def __init__(self, pca_manager, leg_name):
        self.pca = pca_manager
        self.name = leg_name
        self.channels = LEG_CHANNELS[leg_name]

        self.current_angles = {
            "coxa": SERVO_CALIBRATION[(leg_name, "coxa")]["neutral"],
            "femur": SERVO_CALIBRATION[(leg_name, "femur")]["neutral"],
            "tibia": SERVO_CALIBRATION[(leg_name, "tibia")]["neutral"],
        }

    def _apply_calibration(self, joint, angle):
        cal = SERVO_CALIBRATION[(self.name, joint)]
        angle = max(cal["min"], min(cal["max"], angle))
        if cal["invert"]:
            angle = 180 - angle
        return angle

    def set_joint(self, joint, angle):
        calibrated_angle = self._apply_calibration(joint, angle)
        logical_channel = self.channels[joint]
        self.pca.set_angle_logical(logical_channel, calibrated_angle)
        self.current_angles[joint] = angle

    def set_pose(self, coxa=None, femur=None, tibia=None):
        if coxa is not None:
            self.set_joint("coxa", coxa)
        if femur is not None:
            self.set_joint("femur", femur)
        if tibia is not None:
            self.set_joint("tibia", tibia)

    def go_neutral(self):
        self.set_pose(
            coxa=SERVO_CALIBRATION[(self.name, "coxa")]["neutral"],
            femur=SERVO_CALIBRATION[(self.name, "femur")]["neutral"],
            tibia=SERVO_CALIBRATION[(self.name, "tibia")]["neutral"],
        )
