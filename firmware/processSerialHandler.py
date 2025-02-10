# src/hardware/serialhandler/processSerialHandler.py

from templates.workerprocess import WorkerProcess
import serial
from firmware.threads.threadRead import threadRead
from firmware.threads.threadWrite import threadWrite
import logging
import time

class processSerialHandler(WorkerProcess):
    """
    Proces za komunikaciju sa Nucleo pločom putem serijskog porta.
    """
    def __init__(self, queueList, logger, debugging=False):
        # Prvo pozovi __init__ roditeljske klase WorkerProcess
        super(processSerialHandler, self).__init__(queueList)
        self.logger = logger
        self.debugging = debugging
        self._running = True
        # Ne kreiramo serijski port ovde, već u run() – kako bi se izbegle pickling i
        # interni atributi multiprocessing.Process koji se postavljaju u __init__.

    def _init_threads(self):
        if self.serialCom:
            readThread = threadRead(self.serialCom, self.queuesList, self.logger, self.debugging)
            self.threads.append(readThread)
            writeThread = threadWrite(self.serialCom, self.queuesList, self.logger, self.debugging)
            self.threads.append(writeThread)

    def run(self):
        # Inicijalizuj serijski port u child procesu
        try:
            self.serialCom = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.1)
            self.serialCom.flushInput()
            self.serialCom.flushOutput()
            self.logger.info("SerialHandler: Serijski port otvoren na /dev/ttyACM0")
        except Exception as e:
            self.logger.error("SerialHandler: Greška pri otvaranju serijskog porta: %s", e)
            self.serialCom = None

        self._init_threads()
        for thread in self.threads:
            thread.start()
        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False
        for thread in self.threads:
            if hasattr(thread, 'stop'):
                thread.stop()

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("SerialHandler")
    proc = processSerialHandler({}, logger)
    proc.start()
