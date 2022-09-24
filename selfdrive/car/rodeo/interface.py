from os import stat
from typing import List, Tuple
from selfdrive.car import get_safety_config, scale_rot_inertia, scale_tire_stiffness
from selfdrive.car.interfaces import CarInterfaceBase
from cereal import car
from selfdrive.config import Conversions


class CarInterface(CarInterfaceBase):
    def __init__(self, CP, CarController, CarState):
        super().__init__(CP, CarController, CarState)

    @staticmethod
    def get_params(candidate=None, fingerprint=None, car_fw=None):
        ret = CarInterfaceBase.get_std_params(candidate, fingerprint)
        ret.carName = "rodeo"
        ret.safetyConfigs = [
            get_safety_config(
                car.CarParams.SafetyModel.elm327,
                0  # Connect to OBD port
            )
        ]

        ret.wheelbase = 3.2 # m
        ret.centerToFront = ret.wheelbase * 0.5
        ret.mass = 1859 + (0.84 * 76) + 75 # tare + diesel + driver
        ret.steerRatio = 1 # unused
        ret.steerRateCost = 1.0
        ret.steerActuatorDelay = 0.1  # Default delay, not measured yet
    
        ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=1)
        ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)

        ret.minSteerSpeed = 255
        ret.stoppingControl = False
        ret.pcmCruise = False
        ret.openpilotLongitudinalControl = True

        return ret

    def update(self, c: car.CarControl, can_strings: List[bytes]) -> car.CarState:
        # self.cp is a can parser
        self.cp.update_strings(can_strings)

        ret = self.CS.update(self.cp)

        events = self.create_common_events(ret)
        ret.events = events.to_msg()

        # copy back carState packet to CS
        self.CS.out = ret.as_reader()

        return self.CS.out

    def apply(self, c: car.CarControl) -> Tuple[car.CarControl.Actuators, List[bytes]]:
        actuators = car.CarControl.Actuators.new_message()
        return actuators, []


