"""Implements functionality unique to the Lake Shore Model 340 AC bridge and temperature controller.
NOTE: This is an incomplete implmentation that only supports serial, be sure to check the enums to make sure the desired device setting is defined.
"""
from .model_340_enums import Model340Enums
from .temperature_controllers import TemperatureController, StandardEventRegister
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

Model340ServiceRequestEnable = Model340StatusByteRegister


## Controller class def ##
class Model340(TemperatureController, Model340Enums):
    """
    Implements the Model 340 high-level API. Incomplete, check enums.
    """
    vid_pid = []

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

        # Call the parent init, then fill in values specific to the 372
        TemperatureController.__init__(self, serial_number, com_port, baud_rate, timeout, ip_address,
                                       tcp_port, **kwargs)
        
        # Set the vid_pid INSTANCE value. This is different from USB/TCP implementations
        # since although the VID/PID value for a SKU is common to all instances of the SKU, they have a
        # unique serial number to help uniquely identify an instance in cases where multiple devices 
        # connected to one PC.
        # In this case, we're assuming the 340 will be connected by a serial-to-USB adapter, which
        # could appear as a different VID/PID depending on the model (serial number is still necessary
        # in cases of duplicate adapters!)
        self.vid_pid = [(vid, pid)]