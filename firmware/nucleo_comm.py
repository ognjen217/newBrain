import logging
import time
import serial

class NucleoComm:
    def __init__(self, config):
        """
        Initialize communication with the Nucleo board via serial.
        :param config: Dictionary with keys 'port' and 'baudrate'.
        """
        self.config = config
        self.logger = logging.getLogger("NucleoComm")
        self.port = config.get("port", "/dev/ttyACM0")
        self.baudrate = config.get("baudrate", 115200)
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connection = self.ser  # Set connection attribute for status
            self.logger.info("Serial port %s opened at %s baud.", self.port, self.baudrate)
        except Exception as e:
            self.logger.error("Error opening serial port %s: %s", self.port, e)
            self.ser = None
            self.connection = None

    def send_command(self, command, terminator="\r\n", response_wait=1.0):
        """
        Sends a command string to the Nucleo board.
        :param command: Command string (e.g., "SET_SPEED 5").
        :param terminator: String to append to the command (default: "\r\n").
        :param response_wait: Time to wait (in seconds) for a response.
        :return: List of response lines, or an empty list if none.
        """
        if self.ser is None:
            self.logger.error("Serial port not available.")
            return None
        try:
            full_command = command.strip() + terminator
            self.logger.info("Sending command (raw): %s", full_command.encode('utf-8'))
            self.ser.write(full_command.encode('utf-8'))
            self.logger.info("Command sent: %s", full_command.strip())
            # Wait a bit for response
            time.sleep(response_wait)
            responses = []
            while True:
                line = self.ser.readline().decode('utf-8').strip()
                if not line:
                    break
                responses.append(line)
            self.logger.info("Received responses: %s", responses)
            return responses
        except Exception as e:
            self.logger.error("Error sending command '%s': %s", command, e)
            return None

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.info("Serial port closed.")
