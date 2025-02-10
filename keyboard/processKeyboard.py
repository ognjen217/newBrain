import sys
import tty
import termios
import multiprocessing
import time

class processKeyboard(multiprocessing.Process):
    """
    Proces koji osluškuje pritiske tastera (W, A, S, D) i stavlja poruku u prosleđeni queue.
    """
    def __init__(self, queue, logger, debugging=False):
        super(processKeyboard, self).__init__()
        self.queue = queue
        self.logger = logger
        self.debugging = debugging
        self._running = True

    def run(self):
        # Proveri da li je stdin interaktivan (tty)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            while self._running:
                ch = sys.stdin.read(1)
                if ch == '\x03':  # Ctrl+C
                    self.stop()
                    break
                if ch.lower() in ['w', 'a', 's', 'd']:
                    message = {"source": "keyboard", "command": ch.lower()}
                    self.queue.put(message)
                    if self.debugging:
                        self.logger.info("Keyboard: poslat %s", message)
                time.sleep(0.01)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def stop(self):
        self._running = False

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("Keyboard")
    q = multiprocessing.Queue()
    pk = processKeyboard(q, logger, debugging=True)
    pk.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pk.stop()
