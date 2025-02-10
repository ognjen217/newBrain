# firmware/nucleo_comm.py

import serial
import time
import logging

logger = logging.getLogger("NucleoComm")

class NucleoComm:
    def __init__(self, config):
        # Konfiguracija iz config fajla (ako postoji)
        self.port = config.get("port", "/dev/ttyUSB0")
        self.baudRate = config.get("baudRate", 115200)
        try:
            self.ser = serial.Serial(path=self.port, baudRate=self.baudRate, timeout=0.1)
            self.ser.flushInput()
            self.ser.flushOutput()
            logger.info("NucleoComm: Serijski port otvoren na %s", self.port)
        except Exception as e:
            logger.error("NucleoComm: Greška pri otvaranju porta: %s", e)
            self.ser = None

    def send_command(self, command):
        if self.ser:
            try:
                logger.info("NucleoComm: Slanje komande: %s", command.strip())
                self.ser.write(command.encode())
                # Čekanje na odgovor (ako je potrebno)
                time.sleep(0.05)
                response = self.ser.readline().decode(errors='ignore').strip()
                logger.info("NucleoComm: Odgovor: %s", response)
                return response
            except Exception as e:
                logger.error("NucleoComm: Greška pri slanju komande: %s", e)
                return None
        else:
            logger.error("NucleoComm: Serijski port nije otvoren.")
            return None

if __name__ == "__main__":
    # Test primer
    config = {"port": "/dev/ttyACM0", "baudRate": 115200}
    nucleo = NucleoComm(config)
    if nucleo.ser:
        response = nucleo.send_command("#speed:100;;\r\n")
        print("Response:", response)
    else:
        print("Serijski port nije dostupan.")
