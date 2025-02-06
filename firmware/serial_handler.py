# firmware/serial_handler.py
import threading
import serial
import logging
import time
import queue
from firmware.threads.threadRead import ThreadRead

class SerialHandler:
    def __init__(self, port, baudrate=115200, timeout=1, terminator=b';;\r\n'):
        """
        Inicijalizira serijski port i pokreće nit za čitanje.
        Terminator BFMC protokola: ";;\r\n"
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.terminator = terminator
        self.logger = logging.getLogger("SerialHandler")
        self.serial = None
        self.running = False
        self.rx_queue = queue.Queue()
        self.read_thread = None
        self.initialize_serial()

    def initialize_serial(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.logger.info("Serial port %s opened at %s baud.", self.port, self.baudrate)
            self.running = True
            # Pokreni nit za čitanje – implementirana u firmware/threads/threadRead.py
            self.read_thread = ThreadRead(self.serial, self.terminator, self.rx_queue, self.logger)
            self.read_thread.start()
        except Exception as e:
            self.logger.error("Error opening serial port %s: %s", self.port, e)
            self.serial = None

    def send_command(self, command):
        """
        Šalje BFMC-formatiranu komandu na serijski port.
        Očekuje se da komanda već ima ispravan format (npr. "#speed:100;;\r\n").
        """
        if self.serial is None:
            self.logger.error("Serial port not available.")
            return
        try:
            # Resetiramo ulazni buffer kako bismo izbjegli miješanje starih podataka
            self.serial.reset_input_buffer()
            self.logger.debug("Sending command: %s", command)
            self.serial.write(command.encode('utf-8'))
        except Exception as e:
            self.logger.error("Error sending command '%s': %s", command, e)

    def get_messages(self):
        """
        Vraća sve primljene poruke iz queuea i prazni queue.
        """
        msgs = []
        while not self.rx_queue.empty():
            msgs.append(self.rx_queue.get())
        return msgs

    def close(self):
        self.running = False
        if self.read_thread:
            self.read_thread.stop()
            self.read_thread.join(timeout=1)
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Serial port closed.")
