import logging
import time

class NucleoComm:
    def __init__(self, config):
        """
        Inicijalizacija komunikacije sa Nucleo pločom.
        :param config: Rečnik sa parametrima, npr.:
            {
                "port": "/dev/ttyUSB0",
                "baudrate": 115200
            }
        """
        self.config = config
        self.logger = logging.getLogger("NucleoComm")
        self.port = config.get("port", "/dev/ttyUSB0")
        self.baudrate = config.get("baudrate", 115200)
        self.logger.info("NucleoComm inicijalizovan na portu: %s, baudrate: %s", self.port, self.baudrate)
        self.connection = self._connect()

    def _connect(self):
        """
        Uspostavlja konekciju sa Nucleo pločom.
        Ovaj metod koristi placeholder logiku – u praksi, koristiti odgovarajuću biblioteku (npr. pySerial).
        """
        self.logger.info("Uspostavljanje veze sa Nucleo pločom...")
        # Simulirana konekcija
        connection = {"status": "connected", "port": self.port, "baudrate": self.baudrate}
        self.logger.info("Veza uspostavljena: %s", connection)
        return connection

    def send_command(self, command):
        """
        Šalje komandu Nucleo ploči.
        :param command: Komanda koja treba da se pošalje (string ili strukturirani podatak).
        :return: Simulirani odgovor.
        """
        self.logger.info("Slanje komande: %s", command)
        # Simulacija slanja komande – u stvarnoj implementaciji poslati preko serijske veze
        time.sleep(0.05)  # Simuliramo kašnjenje
        response = {"status": "ok", "command": command}
        self.logger.info("Odgovor od Nucleo ploče: %s", response)
        return response

    def close_connection(self):
        """
        Zatvara konekciju sa Nucleo pločom.
        """
        self.logger.info("Zatvaranje veze sa Nucleo pločom.")
        # U stvarnoj implementaciji, zatvoriti serijski port ili sličan resurs
        self.connection = None
