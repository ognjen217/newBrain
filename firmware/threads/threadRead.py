# firmware/threads/threadRead.py

import threading
import time

class ThreadRead(threading.Thread):
    def __init__(self, serial_instance, terminator, rx_queue, logger, name="ThreadRead"):
        super().__init__(name=name)
        self.serial = serial_instance
        self.terminator = terminator
        self.rx_queue = rx_queue
        self.logger = logger
        self._running = True
        self.buffer = b""

    def run(self):
        self.logger.info("ThreadRead started.")
        while self._running:
            try:
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    self.buffer += data
                    # Dok god se u bufferu nalazi terminator, izvuci kompletne poruke
                    while self.terminator in self.buffer:
                        index = self.buffer.index(self.terminator)
                        # Odvoji poruku
                        raw_line = self.buffer[:index].decode('utf-8', errors='ignore').strip()
                        self.buffer = self.buffer[index + len(self.terminator):]
                        # Ovdje možeš dodati dodatnu parsiranje ako je potrebno (npr. prepoznati akciju)
                        self.rx_queue.put(raw_line)
                        self.logger.debug("Received message: %s", raw_line)
                else:
                    time.sleep(0.01)
            except Exception as e:
                self.logger.error("Error in ThreadRead: %s", e)
                time.sleep(0.1)
        self.logger.info("ThreadRead stopped.")

    def stop(self):
        self._running = False
