import logging
import time

class NucleoComm:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("NucleoComm")
        self.port = config.get("port", "/dev/ttyUSB0")
        self.baudrate = config.get("baudrate", 115200)
        self.logger.info("NucleoComm inicijalizovan na portu: %s, baudrate: %s", self.port, self.baudrate)
        self.connection = self._connect()

    def _connect(self):
        self.logger.info("Uspostavljanje veze sa Nucleo pločom...")
        # Simulirana konekcija – u stvarnoj implementaciji koristiti pySerial ili sličnu biblioteku
        connection = {"status": "connected", "port": self.port, "baudrate": self.baudrate}
        self.logger.info("Veza uspostavljena: %s", connection)
        return connection

    def send_command(self, command):
        self.logger.info("Slanje komande: %s", command)
        # Simuliramo kašnjenje i odgovor
        time.sleep(0.05)
        response = {"status": "ok", "command": command}
        self.logger.info("Odgovor od Nucleo ploče: %s", response)
        return response

    def close_connection(self):
        self.logger.info("Zatvaranje veze sa Nucleo pločom.")
        self.connection = None
