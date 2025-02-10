import cv2
import time
import os
from multiprocessing import Process

class processCamera(Process):
    def __init__(self, queueList, logger, debugging=False):
        super(processCamera, self).__init__()
        self.queueList = queueList
        self.logger = logger
        self.debugging = debugging
        self._running = True
        # Definiši putanju za sačuvani frejm
        # Pretpostavljamo da je dashboard frontend u: newBrain/frontend/front/
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "front", "latest.jpg")

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.logger.error("processCamera: Kamera nije otvorena!")
            return
        while self._running:
            ret, frame = cap.read()
            if ret:
                self.logger.info("processCamera: Frame snimljen")
                cv2.imwrite(self.output_path, frame)
                self.queueList["General"].put({
                    "source": "camera",
                    "motorSpeed": "80 rpm",
                    "steeringAngle": "15°",
                    "command": "kamera frame"
                })
            else:
                self.logger.error("processCamera: Nije dobijen frejm")
            time.sleep(0.1)
        cap.release()

    def stop(self):
        self._running = False

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("Camera")
    processCamera({}, logger).run()
