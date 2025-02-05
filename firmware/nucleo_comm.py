import logging
import time
from firmware.serial_handler import SerialHandler

class NucleoComm:
    def __init__(self, config):
        """
        Initializes Nucleo communication using SerialHandler.
        :param config: Dictionary with keys 'port' and 'baudrate'.
        """
        self.config = config
        self.logger = logging.getLogger("NucleoComm")
        self.port = config.get("port", "/dev/ttyACM0")
        self.baudrate = config.get("baudrate", 115200)
        self.terminator = b'\n'  # Using newline as terminator (as in the original BFMC protocol)
        try:
            self.serial_handler = SerialHandler(self.port, self.baudrate, timeout=1, terminator=self.terminator)
            self.connection = self.serial_handler.serial  # For status reporting
            self.logger.info("SerialHandler initialized on %s", self.port)
        except Exception as e:
            self.logger.error("Error initializing SerialHandler: %s", e)
            self.serial_handler = None
            self.connection = None

    def send_command(self, command, response_wait=1.0):
        """
        Sends a command via SerialHandler and returns any responses.
        :param command: Command string (e.g., "SPEED:10").
        :param response_wait: Time to wait for a response.
        :return: List of response messages.
        """
        if self.serial_handler is None:
            self.logger.error("Serial handler not available.")
            return None
        try:
            # Clear old messages before sending
            self.serial_handler.get_messages()
            self.serial_handler.send_command(command)
            self.logger.info("Command sent: %s", command)
            time.sleep(response_wait)
            responses = self.serial_handler.get_messages()
            self.logger.info("Received responses: %s", responses)
            return responses
        except Exception as e:
            self.logger.error("Error sending command '%s': %s", command, e)
            return None

    def close(self):
        if self.serial_handler:
            self.serial_handler.close()
