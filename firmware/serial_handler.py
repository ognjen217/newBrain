# File: firmware/serial_handler.py   (ili gdje već držite SerialHandler)

import threading
import serial
import logging
import time
import re
import os

# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE


class MessageConverter:
    """Creates the message to be sent over the serial communication

    Allowed commands are represented in the field "command".
    Each key of the dictionary represent a command. Each command has a list of attributes ,
    a list of attributes types and optionally if enhanced precision is to be used(send more
    digits after the decimal point).

    Implemented commands:

        | 'Command' : [ [ arg_list ],                [precision in digits            [enhanced precision]   ]
        | 'SPEED'   : [ ['f_vel'],                   [2],                            [False]                ] - Speed command -
        | 'STER'    : [ ['f_angle'],                 [3],                            [False]                ] - Steer command -
        | 'BRAK'    : [ ['f_angle' ],                [int],                          [False]                ] - Brake command -
        | 'BTC'     : [ ['capacity' ],               [int],                          [False]                ] - Set battery capacity -
        | 'ENBL'    : [ ['activate' ],               [int],                          [False]                ] - Activate batterylevel -
        | 'ENIS'    : [ ['activate' ],               [int],                          [False]                ] - Activate instant consumption -
        | 'ENRM'    : [ ['activate' ],               [int],                          [False]                ] - Activate resource monitor -
        | 'ENIMU'   : [ ['activate' ],               [int],                          [False]                ] - Activate IMU -
        | 'STS '    : [ ["speed", "time", "steer"]   [int, int, int]                 [False]                ] - Set a speed a timer and a steering angle -
        | 'KL'      : [ ['f_mode'],                  [int],                          [False]                ] - Enable/Diasble functions -
    """

    commands = {
        "speed": [["speed"], [3], [False]],
        "steer": [["steerAngle"], [3], [False]],
        "brake": [["steerAngle"], [3], [False]],
        "batteryCapacity": [["capacity"], [5], [False]],
        "battery": [["activate"], [1], [False]],
        "instant": [["activate"], [1], [False]],
        "resourceMonitor": [["activate"], [1], [False]],
        "imu": [["activate"], [1], [False]],
        "vcd": [["speed", "steer", "time"], [3, 3, 3], [False]],
        "kl": [["mode"], [2], [False]]
    }
    """ The 'commands' attribute is a dictionary, which contains key word and the acceptable format for each action type. """

    # ===================================== GET COMMAND ===================================
    def get_command(self, action, **kwargs):
        """This method generates automatically the command string, which will be sent to the other device.

        Parameters
        ----------
        action : string
            The key word of the action, which defines the type of action.
        **kwargs : dict
            Optional keyword parameter, which have to contain all parameters of the action.


        Returns
        -------
        string
            Command with the decoded action, which can be transmite to embed device via serial communication.
        """
        valid = self.verify_command(action, kwargs)
        if valid:
            enhPrec = MessageConverter.commands[action][2][0]
            listKwargs = MessageConverter.commands[action][0]

            command = "#" + action + ":"

            for key in listKwargs:
                value = kwargs.get(key)
                command += str(value)+";"

            command += ";\r\n"
            return command
        else:
            return "error"

    # ===================================== VERIFY COMMAND ===============================
    def verify_command(self, action, commandDict):
        """The purpose of this method to verify the command, the command has the right number and named parameters.

        Parameters
        ----------
        action : string
            The key word of the action.
        commandDict : dict
            The dictionary with the names and values of command parameters, it has to contain all parameters defined in the commands dictionary.
        """
        if len(commandDict.keys()) != len(MessageConverter.commands[action][0]):
            print( "Number of arguments does not match" + str(len(commandDict.keys())), str(len(MessageConverter.commands[action][0])))
            return False
        for i, [key, value] in enumerate(commandDict.items()):
            if key not in MessageConverter.commands[action][0]:
                print(action + " should not contain key: " + key)
                return False
            elif type(value) != int:
                print(action + " should be of type int instead of " + str(type(value)))
                return False
            elif value<0 and len(str(value)) > (MessageConverter.commands[action][1][i]+1):
                print(action + " should have " + str(MessageConverter.commands[action][1][i]) + " digits ")
                return False
            elif value>0 and len(str(value)) > MessageConverter.commands[action][1][i]:
                print(action + " should have " + str(MessageConverter.commands[action][1][i]) + " digits ")
                return False

        return True



converter = MessageConverter()

def map_key_to_command(key):
    """
    Mapira tipke W, S, A, D u odgovarajuće BFMC komande koristeći MessageConverter.
    Primjerice:
      - W: vozi naprijed (speed = 100)
      - S: vozi unatrag (speed = -100)
      - A: skreni ulijevo (steerAngle = -25)
      - D: skreni udesno (steerAngle = 25)
    """
    if key.upper() == 'W':
        # Generiramo komandu "speed" – imat ćemo dictionary parametara s ključem "speed"
        return converter.get_command("speed", speed=100)
    elif key.upper() == 'S':
        return converter.get_command("speed", speed=-100)
    elif key.upper() == 'A':
        return converter.get_command("steer", steerAngle=-25)
    elif key.upper() == 'D':
        return converter.get_command("steer", steerAngle=25)
    elif key.upper() in ['KL0', 'KL15', 'KL30']:
        # kl: <broj> -> int
        val_str = key.upper().replace("KL", "")  # "0","15","30"
        kl_val = int(val_str)
        return converter.get_command("kl", mode=kl_val)
    else:
        return None


class SerialHandler:
    def __init__(self, port, baudrate=115200, timeout=1, terminator=b';;\n'):
        """
        Initializes the serial port and starts a thread to continuously read incoming messages.
        :param port: Serial port (e.g., '/dev/ttyACM0').
        :param baudrate: Baud rate (default 115200).
        :param timeout: Read timeout.
        :param terminator: Byte sequence indicating end of message.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.terminator = terminator
        self.logger = logging.getLogger("SerialHandler")
        self.serial = None
        self.running = False
        self.read_thread = None

        # Ovdje ćemo spremati dolazne, **već parsirane** poruke
        self.incoming_messages = []
        self.lock = threading.Lock()

        # Uzorci iz starog BFMC koda, za "resourceMonitor" i "warning"
        self.warningPattern = r'^(-?[0-9]+)H(-?[0-5]?[0-9])M(-?[0-5]?[0-9])S$'
        self.resourceMonitorPattern = r'Heap \((\d+\.\d+)\);Stack \((\d+\.\d+)\)'

        self.initialize_serial()

    def initialize_serial(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.logger.info("Serial port %s opened at %s baud.", self.port, self.baudrate)
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
        except Exception as e:
            self.logger.error("Error opening serial port %s: %s", self.port, e)
            self.serial = None

    def _read_loop(self):
        """Continuously reads from the serial port and buffers complete messages."""
        buffer = b""
        while self.running:
            try:
                if self.serial and self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    buffer += data

                    # Provjera ima li u bufferu terminator (\n)
                    while self.terminator in buffer:
                        index = buffer.index(self.terminator)
                        raw_line = buffer[:index].decode('utf-8', errors='ignore').strip()
                        buffer = buffer[index + len(self.terminator):]

                        self.logger.debug("Raw line received: %s", raw_line)
                        # Nakon što imamo cijeli "line", parsiraj BFMC-style i ubaci u incoming_messages
                        parsed_msg = self._parse_bfmc_style(raw_line)
                        if parsed_msg is not None:
                            with self.lock:
                                self.incoming_messages.append(parsed_msg)
                else:
                    time.sleep(0.01)
            except Exception as e:
                self.logger.error("Error reading from serial port: %s", e)
                time.sleep(0.1)

    def _parse_bfmc_style(self, line):
        """
        Parsira liniju prema BFMC logici iz threadRead.py (sendqueue).
        Vraca dict s poljima:
          {
            "action": ...,
            "value": ... (moze biti float, dict, ili sto već),
            "raw": originalni line
          }
        ili None ako ne odgovara formatu.
        """
        # Ocekivani format: '@akcija:vrijednost;;'  (npr. "@speed:100;;")
        # Minimalni uslov: mora sadrzati '@' i ':'
        if '@' not in line or ':' not in line:
            return None

        # Podijelimo:  @action:value[;;]
        try:
            # 1) odvoji action i value
            #    npr. "@speed:100;;" => action="@speed", value="100;;"
            left, right = line.split(":", 1)
            action = left[1:]  # maknemo '@' -> "speed"
            # Vjerovatno ima ";;" na kraju, pa ga maknemo:
            if right.endswith(";;"):
                right = right[:-2]

            value = right.strip()

            # Sada kreće logika iz BFMC "sendqueue"
            # Ovisno o action = ["imu", "speed", "steer", "instant", "battery", "resourceMonitor", "warning", "shutdown"]
            if action == "imu":
                # Može biti IMU podaci ili ack
                splittedVal = value.split(";")
                # npr. "12;1;0;0.1;0.2;9.81"
                if len(splittedVal) >= 6:
                    # Imamo roll, pitch, yaw, accelx, accely, accelz
                    data = {
                        "roll": splittedVal[0],
                        "pitch": splittedVal[1],
                        "yaw": splittedVal[2],
                        "accelx": splittedVal[3],
                        "accely": splittedVal[4],
                        "accelz": splittedVal[5],
                    }
                    return {"action": "imu_data", "value": data, "raw": line}
                else:
                    # inače je to ack tipa "imu:ack"
                    return {"action": "imu_ack", "value": splittedVal[0], "raw": line}

            elif action == "speed":
                # npr. @speed:100;; -> "100"
                # moze imati i vise polja: "100,xx"?
                speedVal = value.split(",")[0]
                if self._is_float(speedVal):
                    return {"action": "speed", "value": float(speedVal), "raw": line}
                else:
                    return None

            elif action == "steer":
                steerVal = value.split(",")[0]
                if self._is_float(steerVal):
                    return {"action": "steer", "value": float(steerVal), "raw": line}
                else:
                    return None

            elif action == "instant":
                # npr. "0" ili "1" -> pretvorimo u float i / 1000
                if value.isdigit():
                    return {"action": "instant", "value": float(value)/1000.0, "raw": line}
                else:
                    return None

            elif action == "battery":
                # npr. "7205" -> pretvorimo u postotak
                if value.isdigit():
                    valInt = int(value)
                    percentage = (valInt - 7200)/12
                    percentage = max(0, min(100, round(percentage)))
                    return {"action": "battery", "value": percentage, "raw": line}
                else:
                    return None

            elif action == "resourceMonitor":
                # npr. 'Heap (20.35);Stack (50.10)'
                matchRes = re.match(self.resourceMonitorPattern, value)
                if matchRes:
                    return {
                        "action": "resourceMonitor",
                        "value": {
                            "heap": matchRes.group(1),
                            "stack": matchRes.group(2)
                        },
                        "raw": line
                    }
                else:
                    return None

            elif action == "warning":
                # npr. '0H5M30S'
                matchWarn = re.match(self.warningPattern, value)
                if matchWarn:
                    return {
                        "action": "warning",
                        "value": {
                            "hours": matchWarn.group(1),
                            "minutes": matchWarn.group(2),
                            "seconds": matchWarn.group(3)
                        },
                        "raw": line
                    }
                else:
                    return None

            elif action == "shutdown":
                # npr. @shutdown: ...
                # Možemo odmah ili samo pripremiti poruku
                # Oprezno ako radite "os.system('sudo shutdown -h now')"
                return {"action": "shutdown", "value": True, "raw": line}

            else:
                # Ako je nepoznato
                return {"action": action, "value": value, "raw": line}

        except Exception as e:
            self.logger.error("BFMC parse error for line '%s': %s", line, e)
            return None

    def _is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def send_command(self, pressed_key):
        cmd = map_key_to_command(pressed_key)
        if cmd and cmd != "error":
             try:
                 self.serial.reset_input_buffer()
                 self.logger.info("Sending command: %s", cmd.encode('utf-8'))
                 self.serial.write(cmd.encode('utf-8'))
             except Exception as e:
                 self.logger.error("Error sending command '%s': %s", cmd, e)
        else:
             self.logger.error("Invalid command generated for key: %s", pressed_key)



    def get_messages(self):
        """
        Retrieves and clears all buffered incoming *parsed* messages.
        :return: List of dictionaries, e.g.
                 [
                   {"action": "speed", "value": 100.0, "raw": "@speed:100;;"},
                   {"action": "imu_data", ...},
                   ...
                 ]
        """
        with self.lock:
            messages = self.incoming_messages.copy()
            self.incoming_messages = []
        return messages

    def close(self):
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=1)
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Serial port closed.")

