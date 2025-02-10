# src/hardware/serialhandler/threads/threadRead.py

import threading
import time

class threadRead(threading.Thread):
    def __init__(self, serialCom, queueList, logger, debugging=False):
        super(threadRead, self).__init__()
        self.serialCom = serialCom
        self.queueList = queueList
        self.logger = logger
        self.debugging = debugging
        self._running = True

    def run(self):
        while self._running:
            if self.serialCom.in_waiting:
                try:
                    data = self.serialCom.readline().decode(errors='ignore').strip()
                    if data:
                        self.logger.info("threadRead: Primljeni podaci: %s", data)
                        self.queueList["General"].put({"source": "serial", "command": data})
                except Exception as e:
                    self.logger.error("threadRead: Greška pri čitanju: %s", e)
            time.sleep(0.05)

    def stop(self):
        self._running = False

if __name__ == "__main__":
    pass
