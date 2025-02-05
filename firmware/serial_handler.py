import threading
import serial
import logging
import time

class SerialHandler:
    def __init__(self, port, baudrate=115200, timeout=1, terminator=b'\n'):
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
        self.incoming_messages = []
        self.lock = threading.Lock()
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
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    buffer += data
                    while self.terminator in buffer:
                        index = buffer.index(self.terminator)
                        # Extract a complete message (decode from bytes to string)
                        msg = buffer[:index].decode('utf-8').strip()
                        buffer = buffer[index + len(self.terminator):]
                        with self.lock:
                            self.incoming_messages.append(msg)
                        self.logger.debug("Received message: %s", msg)
                else:
                    time.sleep(0.01)
            except Exception as e:
                self.logger.error("Error reading from serial port: %s", e)
                time.sleep(0.1)

    def send_command(self, command):
        """
        Sends a command over the serial port.
        The command is appended with the terminator.
        :param command: Command string (e.g., "SPEED:10").
        """
        if self.serial is None:
            self.logger.error("Serial port not available.")
            return
        try:
            # Clear any existing data before sending
            self.serial.reset_input_buffer()
            full_command = command.strip() + self.terminator.decode('utf-8')
            self.logger.info("Sending command: %s", full_command.encode('utf-8'))
            self.serial.write(full_command.encode('utf-8'))
        except Exception as e:
            self.logger.error("Error sending command '%s': %s", command, e)

    def get_messages(self):
        """
        Retrieves and clears all buffered incoming messages.
        :return: List of received messages.
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
