from selfdrive.car.gm.values import CanBus
from selfdrive.car.interfaces import CarStateBase, GearShifter
from opendbc.can.parser import CANParser
from cereal import car
from selfdrive.config import Conversions

class CarState(CarStateBase):
    def __init__(self, CP):
        super().__init__(CP)

    def update(self, can_parser): 
        ret = car.CarState.new_message()
        ret.vEgoRaw = can_parser.vl["ECMVehicleSpeed"]["VehicleSpeed"] * Conversions.KPH_TO_MS
        ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
        ret.standstill = ret.vEgoRaw < 0.01
        ret.gearShifter = GearShifter.drive
        ret.canValid = True
        return ret

    @staticmethod
    def get_can_parser(car_params):
        signals = [
            ("VehicleSpeed", "ECMVehicleSpeed", 0)
        ]

        return CANParser("rodeo", signals, bus = 1, enforce_checks = False)