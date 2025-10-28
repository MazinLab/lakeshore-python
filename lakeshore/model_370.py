"""Implements functionality unique to the Lake Shore Model 370 AC bridge and temperature controller.
NOTE: This is an incomplete implmentation that only supports serial. The available API for the 370 is also
only minimally supported.
"""

from .model_370_enums import Model370Enums
from .temperature_controllers import TemperatureController, StandardEventRegister
from .generic_instrument import RegisterBase

# 370 uses the standard layout for the standard event register
Model370StandardEventRegister = StandardEventRegister


## Unique register layouts ##
class Model370StatusByteRegister(RegisterBase):
    """
    Status byte register is read-only and has flags signaling
    specific reports by the system (Section 6.1.4), if enabled via the
    Service Request Enable Register. The Serivce Request Enable
    Register is isomorphic and will be aliased (it's just read/write).
    Stored here from LSB to MSB.
    """

    bit_names = [
        "",
        "",
        "settle",
        "alarm",
        "error",
        "standard_event_status",
        "service_request",
        "ramp_done",
    ]

    def __init__(
        self,
        ramp_done: bool,
        service_request: bool,
        standard_event_status: bool,
        error: bool,
        alarm: bool,
        settle: bool,
    ):
        self.settle = settle
        self.alarm = alarm
        self.error = error
        self.std_event_status = standard_event_status
        self.service_request = service_request
        self.ramp_done = ramp_done


Model370ServiceRequestEnable = Model370StatusByteRegister


## Controller class def ##
class Model370(TemperatureController, Model370Enums):
    """
    Implements the Model 370 high-level API. Incomplete, check enums.
    """

    # Initialize registers
    _status_byte_register = Model370StatusByteRegister
    _service_request_enable = Model370ServiceRequestEnable

    def __init__(
        self,
        baud_rate: int,
        vid: int,
        pid: int,
        serial_number: str | None = None,
        com_port: str | None = None,
        timeout: float = 2.0,
        ip_address: None = None,  # Not supported on 370
        tcp_port: None = None,  # Not supported on 370
    ):

        # Set instance value of vid_pid since this can change across 340s due to USB-to-Serial converters
        # (as opposed to being the same for devices with built-in USB ports).
        self.vid_pid = [(vid, pid)]

        # Call the parent init, then fill in values specific to the 340
        TemperatureController.__init__(
            self,
            serial_number=serial_number,
            com_port=com_port,
            timeout=timeout,
            baud_rate=baud_rate,
            ip_address=ip_address,
            tcp_port=tcp_port,
        )

    def get_kelvin_reading(self, input_channel):
        """Returns the temperature value in kelvin of the given channel.

        Args:
            input_channel:
                Selects the channel to retrieve measurement.

        """
        return float(self.query(f"RDGK? {input_channel}", check_errors=False))

    def get_sensor_reading(self, input_channel):
        """Returns the sensor reading in Ohms.

        Returns:
            reading (float):
                The raw sensor reading in the units of the connected sensor.

        """
        return float(self.query(f"RDGR? {input_channel}", check_errors=False))
