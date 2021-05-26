# -*- coding: utf-8 -*-
"""Implements functionality unique to the Lake Shore Model 240 channel modules"""
from enum import IntEnum
import serial

from .generic_instrument import GenericInstrument


class Model240Units(IntEnum):
    """Enumerations that specify temperature units"""
    KELVIN = 1
    CELSIUS = 2
    SENSOR = 3
    FAHRENHEIT = 4


class Model240CurveFormat(IntEnum):
    """Enumerations that specify temperature sensor curve format units"""
    VOLTS_PER_KELVIN = 2
    OHMS_PER_KELVIN = 3
    LOG_OHMS_PER_KELVIN = 4


class Model240Coefficients(IntEnum):
    """Enumerations that specify a positive or negative coefficient"""
    NEGATIVE = 1
    POSITIVE = 2


class Model240SensorTypes(IntEnum):
    """Enumerations specify types of temperature sensors"""
    DIODE = 1
    PLATINUM_RTD = 2
    NTC_RTD = 3


class Model240BrightnessLevel(IntEnum):
    """Enumerations for the screen brightness levels"""
    OFF = 0
    LOW = 25
    MED_LOW = 50
    MED_HIGH = 75
    HIGH = 100


class Model240TemperatureCoefficient(IntEnum):
    """Enumerations specify positive/negative temperature sensor curve coefficients"""
    NEGATIVE = 1
    POSITIVE = 2


class Model240InputRange(IntEnum):
    """Enumerations to specify the input range when autorange is off"""
    RANGE_DIODE = 0
    RANGE_PTRTD_1_KIL_OHMS = 0
    RANGE_NTCRTD_10_OHMS = 0
    RANGE_NTCRTD_30_OHMS = 1
    RANGE_NTCRTD_100_OHMS = 2
    RANGE_NTCRTD_1_KIL_OHMS = 4
    RANGE_NTCRTD_3_KIL_OHMS = 5
    RANGE_NTCRTD_10_KIL_OHMS = 6
    RANGE_NTCRTD_30_KIL_OHMS = 7
    RANGE_NTCRTD_100_KIL_OHMS = 8


class Model240CurveHeader:
    """A class that configures the user curve header and corresponding parameters"""

    def __init__(self, curve_name, serial_number, curve_data_format, temperature_limit, coefficient):
        """Constructor for CurveHeader class

            Args:
                curve_name (str):
                    * Specifies curve name (limit of 15 characters)

                serial_number (str):
                    * Specifies curve serial number (limit of 10 characters)

                curve_data_format (Model240CurveFormat):
                    * Specifies the curve data format

                temperature_limit (float):
                    * Specifies the curve temperature limit in Kelvin

                coefficient (Model240TemperatureCoefficient):
                    * Specifies the curve temperature coefficient

        """

        self.curve_name = curve_name
        self.serial_number = serial_number
        self.curve_data_format = curve_data_format
        self.temperature_limit = temperature_limit
        self.coefficient = coefficient


class Model240InputParameter:
    """Class used to retrieve and set an input channel's parameters and initial settings."""

    def __init__(self, sensor, auto_range_enable, current_reversal_enable, units, input_enable, input_range=None):
        """The constructor for InputParameter class.

            Args:

                sensor (Model240SensorTypes):
                    * Specifies the type of sensor configured at the input
                    * Member of the Model240SensorTypes IntEnum class

                auto_range_enable (bool):
                    Specifies if autoranging is enabled

                current_reversal_enable (bool):
                    * Specifies channel current reversal
                    * Current reversal is used to remove thermal EMF errors on resistive sensors.
                    * Always False if channel is a diode
                    * False = OFF, True = ON

                units (Model240Units):
                    * Member of the Model240Units IntEnum class
                    * Specifies the preferred units parameter.

                input_enable (bool):
                    Specifies whether the channel is disabled or enabled

                input_range (Model240InputRange):
                    Specifies channel range when autorange is off

        """

        self.sensor_type = sensor
        self.temperature_unit = units
        self.auto_range_enable = auto_range_enable
        self.current_reversal_enable = current_reversal_enable
        self.input_enable = input_enable
        self.input_range = input_range


class Model240ProfiSlot:
    """Class used to configure and retrieve data for given PROFIBUS slot."""

    def __init__(self, channel, temp_unit):
        """The constructor for Model240ProfiSlot class.

            Args:
                channel (int):
                    Specifies which slot to configure (1-8)

                temp_unit (Model240Units):
                    * Member of Model240Units IntEnum class
                    * Specifies the units to use for the data in this slot

        """

        self.slot_channel = channel
        self.slot_units = temp_unit


class Model240(GenericInstrument):
    """A class object representing the Lake Shore Model 240 channel modules"""

    vid_pid = [(0x1FB9, 0x0205)]

    def __init__(self,
                 serial_number=None,
                 com_port=None,
                 timeout=2.0,
                 **kwargs):
        # Call the parent init, then fill in values specific to the 240.
        GenericInstrument.__init__(self, serial_number, com_port, 115200, 8, 1, serial.PARITY_NONE, False,
                                   False, timeout, None, None, **kwargs)

    def get_identification(self):
        """Returns instrument's identification parameters.

            Returns:
                id (list):
                    List defining instrument's manufacturer, model, instrument serial, firmware version

        """
        id_parameter = self.query("*IDN?").split(",")
        id_list = {'manufacturer': id_parameter[0],
                   'model': id_parameter[1],
                   'serial number': id_parameter[2],
                   'firmware version': id_parameter[3]}

        return id_list

    def set_brightness(self, brightness_level):
        """Sets the brightness for the front panel display

            Args:
                brightness_level (Model240BrightnessLevel):
                    * Display brightness in percent

        """
        self.command("BRIGT {}".format(brightness_level))

    def get_brightness(self):
        """Returns the brightness level of front panel display

            Return:
                brightness_level (Model240BrightnessLevel):
                    * Display brightness in percent

        """
        brightness_level = Model240BrightnessLevel(int(self.query("BRIGT?")))
        return brightness_level

    def get_celsius_reading(self, channel):
        """Returns the temperature value in Celsius of channel selected.

            Args:
                channel (int):
                    Specifies channel (1-8)

        """
        return self.query("CRDG? {}".format(channel))

    def set_factory_defaults(self):
        """Sets all configuration values to factory defaults and resets the instrument"""
        self.command("DFLT 99")

    def get_kelvin_reading(self, channel):
        """Returns the temperature value in Kelvin of channel selected.

            Args:
                channel (int):
                    Specifies channel (1-8)

        """
        return float(self.query("KRDG? {}".format(channel)))

    def get_fahrenheit_reading(self, channel):
        """Returns the temperature value in Farenheit of channel selected

            Args:
                channel (int):
                    Specifies channel (1-8)

        """
        return self.query("FRDG? {}".format(channel))

    def get_sensor_reading(self, input_channel):
        """Returns the sensor reading in the sensor's units.

            Returns:
                reading (float):
                    * The raw sensor reading in the units of the connected sensor

        """
        return float(self.query("SRDG? {}".format(input_channel)))

    def delete_curve(self, curve):
        """Deletes the user curve

            Args:
                curve (int):
                    * Specifies a user curve to delete

        """
        self.command("CRVDEL {}".format(curve))

    def set_curve_header(self, input_channel, curve_header):
        """Configures the user curve header

            Args:
                input_channel (int):
                    * Specifies which input_channel curve to configure
                    * 1 - 8

                curve_header (CurveHeader):
                    * A CurveHeader class object containing the desired curve information

        """
        command_string = "CRVHDR {},{},{},{},{},{}".format(input_channel,
                                                           curve_header.curve_name,
                                                           curve_header.serial_number,
                                                           curve_header.curve_data_format,
                                                           curve_header.temperature_limit,
                                                           curve_header.coefficient)

        self.command(command_string)

    def get_curve_header(self, curve):
        """Returns parameters set on a particular user curve header

            Args:
                curve:
                    * Specifies a curve to retrieve

            Returns:
                header (CurveHeader):
                    * A CurveHeader class object containing the desired curve information

        """
        response = self.query("CRVHDR? {}".format(curve))
        curve_header = response.split(",")
        header = Model240CurveHeader(str(curve_header[0]),
                                     str(curve_header[1]),
                                     Model240CurveFormat(int(curve_header[2])),
                                     float(curve_header[3]),
                                     Model240TemperatureCoefficient(int(curve_header[4])))
        return header

    def set_curve_data_point(self, channel, index, units, temp):
        """Configures a user curve point

            Args:
                channel (int):
                    Specifies which channel curve to configure (1-8)

                index (int):
                    Specifies the points index in the curve (1-200)

                units (float):
                    Specifies sensor units for this point to 6 digits

                temp (float):
                    Specifies the corresponding temperature in Kelvin for this point to 6 digits

        """
        self.command("CRVPT {},{},{},{}".format(channel, index, units, temp))

    def get_curve_data_point(self, channel, index):
        """Returns a standard or user curve data point

            Args:
                channel (int):
                    Specifies channel (1-8)

                index (int):
                    Specifies the points index in the curve (1–200)

        """
        return self.query("CRVPT? {},{}".format(channel, index))

    def set_filter(self, channel, length):
        """Sets the channel filter parameter

            Args:
                channel (int):
                    Specifies which channel to configure (1-8)

                length (int):
                    Specifies the number of 1 ms points to average for each update (1-100)

        """
        self.command("FILTER {},{}".format(channel, length))

    def get_filter(self, channel):
        """Returns the filter parameter

            Args:
                channel (int):
                    Specifies channel (1-8)

        """
        return self.query("FILTER? {}".format(channel))

    def set_sensor_name(self, channel, name):
        """Names the sensor channel in specified channel.

            Args:
                channel (int):
                    Specifies which channel to configure (1-8)

                name (str):
                    Specifies the name to associate with the sensor channel

        """
        self.command("INNAME {},{}".format(channel, name))

    def get_sensor_name(self, channel):
        """Returns the sensor channel's name.

            Args:
                channel (int):
                    Specifies channel (1-8)

        """
        return str(self.query("INNAME? {}".format(channel)))

    def set_input_parameter(self, channel, input_parameter):
        """Sets channel type parameters.

            Args:
                channel (int):
                    Specifies which channel to configure (1-8)

                input_parameter (InputParameter):
                    See InputParameter class

        """
        if input_parameter.auto_range_enable is None:
            input_range = 0
        else:
            input_range = input_parameter.input_range

        command_string = "INTYPE {},{},{},{},{},{},{}".format(channel,
                                                              input_parameter.sensor_type.value,
                                                              int(input_parameter.auto_range_enable),
                                                              input_range,
                                                              int(input_parameter.current_reversal_enable),
                                                              input_parameter.temperature_unit.value,
                                                              int(input_parameter.input_enable))

        self.command(command_string)

    def get_input_parameter(self, channel):
        """Returns channel type parameter details

            Args:
                channel (int):
                    Specifies channel (1-8)

        """
        response = self.query("INTYPE? {}".format(channel))
        data = response.split(",")
        input_parameter = Model240InputParameter(Model240SensorTypes(int(data[0])),
                                                 bool(data[1]),
                                                 bool(data[3]),
                                                 Model240Units(int(data[4])),
                                                 bool(data[5]),
                                                 int(data[2]))
        return input_parameter

    def set_modname(self, name):
        """Names module.

            Args:
                name (str):
                    Specifies the name or description to help identify the module

        """
        self.command("MODNAME {}".format(name))

    def get_modname(self):
        """Returns module name

            Returns:
                modname (str):
                    Specifies name of module

        """
        return self.query("MODNAME?")

    def set_profibus_slot_count(self, count):
        """Configures the number of PROFIBUS slots for the instrument to present to the bus as a modular station

            Args:
                count (int):
                    Specifies the number of PROFIBUS slots (1-8)

        """
        self.command("PROFINUM {}".format(count))

    def get_profibus_slot_count(self):
        """Returns the number of PROFIBUS slots for the instrument present to the bus as a modular station

            Returns:
                slot_count (str):
                    Specifies PROFIBUS slot count

        """
        return self.query("PROFINUM?")

    def set_profibus_address(self, address):
        """Configures the PROFIBUS address for the module. An address of 126 indicates that it is not configured and it
        then can be set by a PROFIBUS master.

            Args:
                address (str):
                    Specifies the PROFIBUS address (1-126)

        """
        self.command("ADDR {}".format(address))

    def get_profibus_address(self):
        """Returns the PROFIBUS address for the module.

            Returns:
                address (str):
                    Specifies PROFIBUS address of module

        """
        return int(self.query("ADDR?"))

    def set_profibus_slot_configuration(self, slot, profislot_config):
        """Configures what data to present on the given PROFIBUS slot. Note that the correct
            number of slots must be configured with the PROFINUM command, or the slot may be ignored.

            Args:
                slot (int):
                    Specifies the slot to be configured

                profislot_config (Model240ProfiSlot):
                    A Model240ProfiSlot class object containing the desired PROFIBUS slot configuration information

        """
        self.command("PROFISLOT {},{},{}".format(slot, profislot_config.slot_channel, profislot_config.slot_units))

    def get_profibus_slot_configuration(self, slot_num):
        """Returns the slot configuration of the slot number.

            Returns:
                slot_config (Model240ProfiSlot):
                    See Model240ProfiSlot class

        """
        response = self.query("PROFISLOT? {}".format(slot_num)).split(",")
        slot_configuration = Model240ProfiSlot(int(response[0]), Model240Units(int(response[1])))
        return slot_configuration

    def get_profibus_connection_status(self):
        """Returns the connection status of PROFIBUS.

            Returns:
                status (str):
                    Specifies connection status of PROFIBUS

        """
        return self.query("PROFISTAT?")

    def get_channel_reading_status(self, channel):
        """The integer returned represents the sum of the bit weighting of the channel status flag
            bits. A “000” response indicates a valid reading is present.

            Args:
                channel (int):
                    Specifies which channel to query (1-8)

            Returns:
                bit_status (dict):
                    Dictionary containing the current status indicator

        """
        bit_status = {}
        bit_names = ["invalid reading",
                     "",
                     "",
                     "",
                     "temp under range",
                     "temp over range",
                     "sensor units over range",
                     "sensor units under range"
                     ]

        status_indicator = int(self.query("RDGST? {}".format(channel)))

        for count, bit_name in enumerate(bit_names):
            mask = 0b1 << count
            bit_status[bit_name] = bool(mask & status_indicator)

        return bit_status

    def get_sensor_units_channel_reading(self, channel):
        """Returns the sensor units value of channel being queried

            Args:
                channel (int):
                    Specifies which channel to query (1-8)

        """
        return self.query("SRDG? {}".format(channel))


__all__ = ['Model240', 'Model240Units', 'Model240CurveFormat', 'Model240Coefficients', 'Model240SensorTypes',
           'Model240BrightnessLevel', 'Model240TemperatureCoefficient', 'Model240InputRange', 'Model240CurveHeader',
           'Model240InputParameter', 'Model240ProfiSlot']
