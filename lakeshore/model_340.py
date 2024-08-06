"""Implements functionality unique to the Lake Shore Model 340 AC bridge and temperature controller."""
from .model_340_enums import Model340Enums
from .temperature_controllers import TemperatureController, StandardEventRegister, OperationEvent
from .generic_instrument import RegisterBase

# 340 uses the standard layout for the standard event register
Model340StandardEventRegister = StandardEventRegister

## Unique register layouts ##
class Model340StatusByteRegister(RegisterBase):
    """
    Status byte register  is read-only and has flags signaling
    specific reports by the system (Pg. 9-3), if enabled via the
    Service Request Enable Register. The Serivce Request Enable
    Register is isomorphic and will be aliased (it's just read/write).
    Stored here from LSB to MSB.
    """
    bit_names = [
        "new_a_and_b",
        "new_opt",
        "settle",
        "alarm",
        "error",
        "standard_event_status",
        "service_request",
        "ramp_done"
    ]

    def __init__(self,
                 ramp_done: bool,
                 service_request: bool,
                 standard_event_status: bool,
                 error: bool,
                 alarm: bool,
                 settle: bool,
                 new_opt: bool,
                 new_a_and_b: bool):
        self.new_ab = new_a_and_b
        self.new_opt = new_opt
        self.settle = settle
        self.alarm = alarm
        self.error = error
        self.std_event_status = standard_event_status
        self.service_request = service_request
        self.ramp_done = ramp_done

Model340ServiceRequestEnableRegister = Model340StatusByteRegister