import cv2
import threading
import base64
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
import os
import psutil
from picamera2 import Picamera2

class FrameBuffer:
    """Simple buffer to store frames and timestamps."""
    def __init__(self):
        if self.queuesList is None:
            self.queuesList = {}

        elif not isinstance(self.queuesList, dict):
            raise TypeError("queuesList must be a dictionary!")

        self.frame = None
        self.timestamp = 0
        self.lock = threading.Lock()
        self.event = threading.Event()

    def update(self, frame):
        with self.lock:
            self.frame = frame
            self.timestamp = time.time()
            self.event.set()

    def get(self):
        with self.lock:
            return self.frame, self.timestamp

    def clear(self):
        self.event.clear()

class ThreadCamera(threading.Thread):
    """Thread that handles camera functionality."""
    def __init__(self, queuesList, logger, debugger):
        super(ThreadCamera, self).__init__()
        self.queuesList = queuesList
        self.logger = logger
        self.debugger = debugger
        self.frame_rate = 16
        self.recording = False
        self.video_writer = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._running = True
        self.frame_buffer_even = FrameBuffer()
        self.frame_buffer_odd = FrameBuffer()
        self._acquisition_running = threading.Event()
        self._acquisition_running.set()
        self._processing_running = threading.Event()
        self._processing_running.set()
        self.camera = Picamera2()
        self._init_camera()
        self.frame_count = 0
        model_path_yolo = os.path.abspath(os.path.join(os.path.dirname(__file__), "best.pt"))
        self.yolo_model = YOLO(model_path_yolo)

    def _init_camera(self):
        """Initializes camera object."""
        config = self.camera.create_preview_configuration(
            buffer_count=1,
            main={"format": "RGB888", "size": (2048, 1080)},
            lores={"format": "YUV420", "size": (512, 270)}
        )
        self.camera.configure(config)
        self.camera.start()
        time.sleep(2)

    def capture_loop(self):
        """Thread that continuously fetches frames from the camera."""
        while self._running and self._acquisition_running.is_set():
            try:
                frame = self.camera.capture_array("main", wait=True)
                self.frame_count = (self.frame_count + 1) % 16
                if self.frame_count % 2 == 0:
                    self.frame_buffer_even.update(frame)
                else:
                    self.frame_buffer_odd.update(frame)
            except Exception as e:
                self.logger.error(f"Capture loop error: {e}")
            time.sleep(0.001)

    def processing_loop_even(self):
        """Thread that processes even frames."""
        while self._running and self._processing_running.is_set():
            if not self.frame_buffer_even.event.wait(timeout=0.005):
                continue
            frame, _ = self.frame_buffer_even.get()
            self.frame_buffer_even.clear()
            if frame is None:
                continue
            processed_frame = self.process_frame(frame)
            if processed_frame is None:
                continue
            _, encodedImg = cv2.imencode(".jpg", processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            encodedImageData = base64.b64encode(encodedImg).decode("utf-8")
            if "processed_output" not in self.queuesList:
                if self.queuesList is not None and isinstance(self.queuesList, dict):
                    if self.queuesList is not None and isinstance(self.queuesList, dict):
                        if "processed_output" not in self.queuesList:
                            if self.queuesList is not None and isinstance(self.queuesList, dict):
                                if "processed_output" not in self.queuesList:
                                    self.queuesList["processed_output"] = threading.Queue()
                                self.queuesList["processed_output"].put({"parity": "even", "image": encodedImageData})
                            else:
                                self.logger.error(f"Invalid queuesList type: {type(self.queuesList)}")

                            self.queuesList["processed_output"].put({"parity": "even", "image": encodedImageData})
                else:
                    self.logger.error("queuesList is not initialized properly in processing_loop_even")

            self.queuesList["processed_output"].put({"parity": "even", "image": encodedImageData})

    def processing_loop_odd(self):
        """Thread that processes odd frames using YOLO."""
        while self._running and self._processing_running.is_set():
            if not self.frame_buffer_odd.event.wait(timeout=0.005):
                continue
            frame, _ = self.frame_buffer_odd.get()
            self.frame_buffer_odd.clear()
            if frame is None:
                continue
            results = self.yolo_model(frame)
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{cls} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            _, encodedImg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            encodedImageData = base64.b64encode(encodedImg).decode("utf-8")
            if "yolo_output" not in self.queuesList:
                if self.queuesList is not None and isinstance(self.queuesList, dict):
                    if self.queuesList is not None and isinstance(self.queuesList, dict):
                        if "yolo_output" not in self.queuesList:
                            self.queuesList["yolo_output"] = threading.Queue()
                        self.queuesList["yolo_output"].put({"parity": "odd", "image": encodedImageData})
                else:
                    self.logger.error(f"Invalid queuesList type: {type(self.queuesList)}")

                self.queuesList["yolo_output"].put({"parity": "odd", "image": encodedImageData})
                else:
                    self.logger.error("queuesList is not initialized properly in processing_loop_odd")

            self.queuesList["yolo_output"].put({"parity": "odd", "image": encodedImageData})

    def process_frame(self, frame):
        """Applies Hough Transform for line detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=20)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return frame

    def run(self):
        """Main method that starts acquisition and processing threads."""
        threading.Thread(target=self.capture_loop).start()
        threading.Thread(target=self.processing_loop_even).start()
        threading.Thread(target=self.processing_loop_odd).start()

    def stop(self):
        """Stops the thread and releases resources."""
        self._running = False
        self._acquisition_running.clear()
        self._processing_running.clear()
