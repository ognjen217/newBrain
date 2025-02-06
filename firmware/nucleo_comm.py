# firmware/nucleo_comm.py

import logging
import time
from firmware.serial_handler import SerialHandler
from firmware.message_converter import MessageConverter

class NucleoComm:
    def __init__(self, config):
        """
        config je dict s ključevima 'port' i 'baudrate'
        """
        self.logger = logging.getLogger("NucleoComm")
        self.port = config.get("port", "/dev/ttyACM0")
        self.baudrate = config.get("baudrate", 115200)
        self.terminator = b';;\r\n'
        try:
            self.serial_handler = SerialHandler(self.port, self.baudrate, timeout=1, terminator=self.terminator)
            self.logger.info("SerialHandler initialized on %s", self.port)
        except Exception as e:
            self.logger.error("Error initializing SerialHandler: %s", e)
            self.serial_handler = None

        self.converter = MessageConverter()

    def send_command(self, command):
        if self.serial_handler:
            self.serial_handler.send_command(command)
        else:
            self.logger.error("No SerialHandler instance available.")

    def send_key_command(self, key):
        """
        Mapira tipke W, A, S, D u BFMC komande:
          W -> "#speed:100;;\r\n"
          S -> "#speed:-100;;\r\n"
          A -> "#steer:-25;;\r\n"
          D -> "#steer:25;;\r\n"
        """
        cmd = None
        if key.upper() == 'W':
            cmd = self.converter.get_command("speed", speed=100)
        elif key.upper() == 'S':
            cmd = self.converter.get_command("speed", speed=-100)
        elif key.upper() == 'A':
            cmd = self.converter.get_command("steer", steerAngle=-25)
        elif key.upper() == 'D':
            cmd = self.converter.get_command("steer", steerAngle=25)
        else:
            self.logger.error("Invalid key: %s", key)
            return

        if cmd != "error":
            self.logger.debug("Generated key command: %s", cmd)
            self.send_command(cmd)
        else:
            self.logger.error("Error generating command for key: %s", key)

    def send_kl_command(self, kl_value):
        """
        Generira komandu za KL – očekivane vrijednosti: 0, 15, 30.
        Primjer: kl_value=15 → "#kl:15;;\r\n"
        """
        cmd = self.converter.get_command("kl", mode=kl_value)
        if cmd != "error":
            self.logger.debug("Generated KL command: %s", cmd)
            self.send_command(cmd)
        else:
            self.logger.error("Error generating KL command for value: %s", kl_value)

    def get_received_messages(self):
        if self.serial_handler:
            return self.serial_handler.get_messages()
        else:
            return []

    def close(self):
        if self.serial_handler:
            self.serial_handler.close()
