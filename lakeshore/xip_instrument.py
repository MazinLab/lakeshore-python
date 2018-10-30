"""This module implements a parent class that contains all functionality shared by Lake Shore XIP instruments."""

from collections import namedtuple

import re
import select
import socket
from time import sleep

import serial
from serial.tools.list_ports import comports


class XIPInstrumentConnectionException(Exception):
    """Names a new type of exception specific to instrument connectivity."""
    pass


class XIPInstrument:
    """Parent class that implements functionality shared by all XIP instruments"""

    vid_pid = []
    status_byte_register = [
        "",
        "",
        "error_available",
        "questionable_summary",
        "message_available_summary",
        "event_status_summary",
        "master_summary",
        "operation_summary"
    ]
    standard_event_register = [
        "operation_complete",
        "query_error",
        "device_specific_error",
        "execution_error",
        "command_error",
        "",
        "power_on"
    ]
    operation_register = []
    questionable_register = []

    StatusByteRegister = namedtuple('StatusByteRegister',
                                    [bit_name for bit_name in status_byte_register if bit_name != ""])

    StandardEventRegister = namedtuple('StandardEventRegister',
                                       [bit_name for bit_name in standard_event_register if bit_name != ""])

    OperationRegister = namedtuple('OperationRegister', [])

    QuestionableRegister = namedtuple('QuestionableRegister', [])

    def __init__(self, serial_number, com_port, baud_rate, flow_control, timeout, ip_address):
        # Initialize values common to all XIP instruments
        self.device_serial = None
        self.device_tcp = None

        # Raise an error if serial and TCP parameters are passed. Otherwise connect to the instrument using one of them.
        if ip_address is not None:
            if com_port is not None:
                raise ValueError("Two different connection methods provided.")
            else:
                self.connect_tcp(ip_address, timeout)
        else:
            self.connect_usb(serial_number, com_port, baud_rate, timeout, flow_control)

        # Query the instrument identification information and store it in variables
        idn_response = self.query('*IDN?', check_errors=False).split(',')
        self.firmware_version = idn_response[3]
        self.serial_number = idn_response[2]
        self.model_number = idn_response[1]

        # Check to make sure the serial number matches what was provided if connecting over TCP
        if ip_address is not None and serial_number is not None and serial_number != self.serial_number:
            raise XIPInstrumentConnectionException("Instrument found but the serial number does not match. " +
                                                   "serial number provided is " + serial_number +
                                                   ", serial number found is " + self.serial_number)

    def __del__(self):
        if self.device_serial is not None:
            self.device_serial.close()
        if self.device_tcp is not None:
            self.device_tcp.close()

    def command(self, *commands, **kwargs):
        """Send a SCPI command or multiple commands to the instrument"""

        check_errors = kwargs.get("check_errors", True)

        # Group all commands into a single string with SCPI delimiters.
        command_string = ";:".join(commands)

        # Pass the string to the query function if it contains a question mark.
        if check_errors:
            # Do a query which will automatically check the errors.
            self.query(command_string)
        else:
            # Send command to the instrument over serial. If serial is not configured, send it over TCP.
            if self.device_serial is not None:
                self._usb_command(command_string)
            elif self.device_tcp is not None:
                self._tcp_command(command_string)
            else:
                raise XIPInstrumentConnectionException("No connections configured")

    def query(self, *queries, **kwargs):
        """Send a SCPI query or multiple queries to the instrument and return the response(s)"""

        check_errors = kwargs.get("check_errors", True)

        # Group all commands and queries a single string with SCPI delimiters.
        query_string = ";:".join(queries)

        # Append the query with an additional error buffer query.
        if check_errors:
            query_string += ";:SYSTem:ERRor:ALL?"

        # Query the instrument over serial. If serial is not configured, use TCP.
        if self.device_serial is not None:
            response = self._usb_query(query_string)
        elif self.device_tcp is not None:
            response = self._tcp_query(query_string)
        else:
            raise XIPInstrumentConnectionException("No connections configured")

        if check_errors:
            # Split the responses to each query, remove the last response which is to the error buffer query,
            # and check whether it contains an error
            response_list = re.split(''';(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', response)
            error_response = response_list.pop()
            self._error_check(error_response)
            response = ';'.join(response_list)

        return response

    @staticmethod
    def _error_check(error_response):
        """Evaluates the instrument response"""

        # If the error buffer returns an error, raise an exception with that includes the error.
        if "No error" not in error_response:
            raise XIPInstrumentConnectionException("SCPI command error(s): " + error_response)

    def connect_tcp(self, ip_address, timeout):
        """Establishes a TCP connection with the instrument on the specified IP address"""
        self.device_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.device_tcp.settimeout(timeout)
        self.device_tcp.connect((ip_address, 8888))

        # Send the instrument a line break, wait 100ms, and clear the input buffer so that
        # any leftover communications from a prior session don't gum up the works.
        self.device_tcp.send(b'\n')
        sleep(0.1)
        while True:
            read_objects, _, _ = select.select([self.device_tcp], [], [], 0.0)
            if not read_objects:
                break
            for read_object in read_objects:
                read_object.recv(1)

    def disconnect_tcp(self):
        """Disconnect the TCP connection"""
        self.device_tcp.close()
        self.device_tcp = None

    def connect_usb(self, serial_number=None, com_port=None, baud_rate=None, timeout=None, flow_control=None):
        """Establish a serial USB connection"""

        # Scan the ports for devices matching the VID and PID combos of the instrument
        for port in comports():
            if (port.vid, port.pid) in self.vid_pid:
                # If the com port argument is passed, check for a match
                if port.device == com_port or com_port is None:
                    # If the serial number argument is passed, check for a match
                    if port.serial_number == serial_number or serial_number is None:
                        # Establish a connection with device using the instrument's serial communications parameters
                        self.device_serial = serial.Serial(port.device,
                                                           baudrate=baud_rate,
                                                           timeout=timeout,
                                                           parity=serial.PARITY_NONE,
                                                           rtscts=flow_control)

                        # Send the instrument a line break, wait 100ms, and clear the input buffer so that
                        # any leftover communications from a prior session don't gum up the works
                        self.device_serial.write(b'\n')
                        sleep(0.1)
                        self.device_serial.reset_input_buffer()

                        break
        else:
            if com_port is None and serial_number is None:
                raise XIPInstrumentConnectionException("No serial connections found")
            else:
                raise XIPInstrumentConnectionException(
                    "No serial connections found with a matching COM port and/or matching serial number")

    def disconnect_usb(self):
        """Disconnect the USB connection"""
        self.device_serial.close()
        self.device_serial = None

    def _tcp_command(self, command):
        """Send a command over the TCP connection"""
        self.device_tcp.send(command.encode('utf-8') + b'\n')

    def _tcp_query(self, query):
        """Query over the TCP connection"""
        self._tcp_command(query)

        total_response = ""

        # Continuously receive data from the buffer until a line break
        while True:

            # Receive the data and raise an error on timeout
            try:
                response = self.device_tcp.recv(4096).decode('utf-8')
            except socket.timeout:
                raise XIPInstrumentConnectionException("Connection timed out")

            # Add received information to the response
            total_response += response

            # Return the response once it ends with a line break
            if total_response.endswith("\r\n"):
                return total_response.rstrip()

    def _usb_command(self, command):
        """Send a command over the serial USB connection"""
        self.device_serial.write(command.encode('ascii') + b'\n')

    def _usb_query(self, query):
        """Query over the serial USB connection"""

        self._usb_command(query)
        response = self.device_serial.readline().decode('ascii')

        # If nothing is returned, raise a timeout error.
        if not response:
            raise XIPInstrumentConnectionException("Communication timed out")

        return response

    def get_status_byte(self):
        """Returns named bits of the status byte register and their values"""
        response = self.query("*STB?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.status_byte_register,
                                                          self.StatusByteRegister)

        return status_register

    def get_service_request_enable_mask(self):
        """Returns the named bits of the status byte service request enable register.
        This register determines which bits propagate to the master summary status bit"""
        response = self.query("*SRE?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.status_byte_register,
                                                          self.StatusByteRegister)

        return status_register

    def set_service_request_enable_mask(self, register_mask):
        """Configures values of the service request enable register bits.
        This register determines which bits propagate to the master summary bit"""
        integer_representation = self._configure_status_register(self.status_byte_register, register_mask)
        self.command("*SRE " + str(integer_representation), check_errors=False)

    def get_standard_events(self):
        """Returns the names of the standard event register bits and their values"""
        response = self.query("*ESR?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.standard_event_register,
                                                          self.StandardEventRegister)

        return status_register

    def get_standard_event_enable_mask(self):
        """Returns the names of the standard event enable register bits and their values.
        These values determine which bits propagate to the standard event register"""
        response = self.query("*ESE?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.standard_event_register,
                                                          self.StandardEventRegister)

        return status_register

    def set_standard_event_enable_mask(self, register_mask):
        """Configures values of the standard event enable register bits.
        These values determine which bits propagate to the standard event register"""
        integer_representation = self._configure_status_register(self.standard_event_register, register_mask)
        self.command("*ESE " + str(integer_representation), check_errors=False)

    def get_present_operation_status(self):
        """Returns the names of the operation status register bits and their values"""
        response = self.query("STATus:OPERation:CONDition?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.operation_register,
                                                          self.OperationRegister)

        return status_register

    def get_operation_events(self):
        """Returns the names of operation event status register bits that are currently high.
        The event register is latching and values are reset when queried."""
        response = self.query("STATus:OPERation:EVENt?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.operation_register,
                                                          self.OperationRegister)

        return status_register

    def get_operation_event_enable_mask(self):
        """Returns the names of the operation event enable register bits and their values.
        These values determine which operation bits propagate to the operation event register."""
        response = self.query("STATus:OPERation:ENABle?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.operation_register,
                                                          self.OperationRegister)

        return status_register

    def set_operation_event_enable_mask(self, register_mask):
        """Configures the values of the operation event enable register bits.
        These values determine which operation bits propagate to the operation event register."""
        integer_representation = self._configure_status_register(self.operation_register, register_mask)
        self.command("STATus:OPERation:ENABle " + str(integer_representation), check_errors=False)

    def get_present_questionable_status(self):
        """Returns the names of the questionable status register bits and their values"""
        response = self.query("STATus:QUEStionable:CONDition?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.questionable_register,
                                                          self.QuestionableRegister)

        return status_register

    def get_questionable_events(self):
        """Returns the names of questionable event status register bits that are currently high.
        The event register is latching and values are reset when queried."""
        response = self.query("STATus:QUEStionable:EVENt?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.questionable_register,
                                                          self.QuestionableRegister)

        return status_register

    def get_questionable_event_enable_mask(self):
        """Returns the names of the questionable event enable register bits and their values.
        These values determine which questionable bits propagate to the questionable event register."""
        response = self.query("STATus:QUEStionable:ENABle?", check_errors=False)
        status_register = self._interpret_status_register(response,
                                                          self.questionable_register,
                                                          self.QuestionableRegister)

        return status_register

    def set_questionable_event_enable_mask(self, register_mask):
        """Configures the values of the questionable event enable register bits.
        These values determine which questionable bits propagate to the questionable event register."""
        integer_representation = self._configure_status_register(self.questionable_register, register_mask)
        self.command("STATus:QUEStionable:ENABle " + str(integer_representation), check_errors=False)

    def reset_status_register_masks(self):
        """Resets status register masks to preset values"""
        self.command("STATus:PRESet", check_errors=False)

    @staticmethod
    def _interpret_status_register(integer_representation, register_bit_names, register):
        """Translates the integer representation of a register state into a named array"""
        # Initialize an empty array.
        bit_states = []

        # Create an array that maps the boolean value of each bit in the integer
        # to the name of the instrument state it represents.
        for count, bit_name in enumerate(register_bit_names):
            if bit_name:
                mask = 0b1 << count
                bit_states.append(bool(int(integer_representation) & mask))

        status_register = register(*bit_states)

        return status_register

    @staticmethod
    def _configure_status_register(register_bit_names, register_mask):
        """Translates from a named array to an integer representation value"""

        # Check whether an integer was passed. If so, return it.
        if isinstance(register_mask, int):
            return register_mask

        # If a namedtuple class was passed, call a function to turn it back into an integer representation
        integer_representation = 0
        number_of_bits = 0

        # Add up the boolean values of a list of named instrument states
        # while being careful to account for unnamed entries in the register bit names list
        for bit_name in register_bit_names:

            if bit_name:
                integer_representation += int(getattr(register_mask, bit_name)) << number_of_bits

            number_of_bits += 1

        return integer_representation

    def modify_service_request_mask(self, bit_name, value):
        """Gets the service request enable mask, changes a bit, and sets the register"""
        status_mask = self.get_service_request_enable_mask()

        new_status_mask = status_mask._replace(**{bit_name: value})

        self.set_service_request_enable_mask(new_status_mask)

    def modify_standard_event_register_mask(self, bit_name, value):
        """Gets the standard event register mask, changes a bit, and sets the register"""
        status_mask = self.get_standard_event_enable_mask()

        new_status_mask = status_mask._replace(**{bit_name: value})

        self.set_standard_event_enable_mask(new_status_mask)

    def modify_operation_register_mask(self, bit_name, value):
        """Gets the operation condition register mask, changes a bit, and sets the register"""
        status_mask = self.get_operation_event_enable_mask()

        new_status_mask = status_mask._replace(**{bit_name: value})

        self.set_operation_event_enable_mask(new_status_mask)

    def modify_questionable_register_mask(self, bit_name, value):
        """Gets the questionable condition register mask, changes a bit, and sets the register"""
        status_mask = self.get_questionable_event_enable_mask()

        new_status_mask = status_mask._replace(**{bit_name: value})

        self.set_questionable_event_enable_mask(new_status_mask)
