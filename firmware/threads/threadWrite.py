import threading
import time

class threadWrite(threading.Thread):
    def __init__(self, serialCom, queueList, logger, debugging=False):
        super(threadWrite, self).__init__()
        self.serialCom = serialCom
        self.queuesList = queueList
        self.logger = logger
        self.debugging = debugging
        self._running = True

    def run(self):
        while self._running:
            if not self.queuesList["General"].empty():
                msg = self.queuesList["General"].get()
                # Obradi samo poruke koje dolaze sa tastature
                if msg.get("source") == "keyboard":
                    key = msg.get("command")
                    command = self.convert_key_to_command(key)
                    if command:
                        self.logger.info("threadWrite: Slanje komande: %s", command.strip())
                        self.serialCom.write(command.encode())
            time.sleep(0.01)

    def convert_key_to_command(self, key):
        mapping = {
            'w': "#speed:100;;\r\n",
            's': "#speed:-100;;\r\n",
            'a': "#steer:-25;;\r\n",
            'd': "#steer:25;;\r\n"
        }
        return mapping.get(key, "")

    def stop(self):
        self._running = False

if __name__ == "__main__":
    pass
