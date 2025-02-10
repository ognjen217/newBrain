# src/gateway/processGateway.py

from multiprocessing import Process
import time

class processGateway(Process):
    def __init__(self, queueList, logger):
        super(processGateway, self).__init__()
        self.queueList = queueList
        self.logger = logger
        self._running = True

    def run(self):
        self.logger.info("Gateway proces pokrenut.")
        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("Gateway")
    processGateway({}, logger).run()
