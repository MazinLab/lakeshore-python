"""Implements functionality unique to the Lake Shore Model 340 AC bridge and temperature controller.
NOTE: This is an incomplete implmentation that only supports serial.
"""
from .model_340_enums import Model340Enums
from .temperature_controllers import TemperatureController, StandardEventRegister
from .generic_instrument import RegisterBase

# 340 uses the standard layout for the standard event register
Model340StandardEventRegister = StandardEventRegister

## Unique register layouts ##
class Model340StatusByteRegister(RegisterBase):
    """
    Status byte register is read-only and has flags signaling
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

Model340ServiceRequestEnable = Model340StatusByteRegister


## Controller class def ##
class Model340(TemperatureController, Model340Enums):
    """
    Implements the Model 340 high-level API. Incomplete, check enums.
    """
    # Initialize registers
    _status_byte_register = Model340StatusByteRegister
    _service_request_enable = Model340ServiceRequestEnable

    def __init__(self,
                 baud_rate: int,
                 vid: hex,
                 pid: hex,
                 serial_number: str | None = None,
                 com_port: str | None = None,
                 timeout: float = 2.0,
                 ip_address: None = None, # Not supported on 340
                 tcp_port: None = None, # Not supported on 340
                 **kwargs):
        
        # Set instance value of vid_pid since this can change across 340s (as opposed to being the same
        # for other devices)
        self.vid_pid = [(vid, pid)]

        # Call the parent init, then fill in values specific to the 340
        TemperatureController.__init__(self, serial_number, com_port, baud_rate, timeout, ip_address,
                                       tcp_port, **kwargs)
    