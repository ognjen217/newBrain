#!/usr/bin/env python
import cv2
import threading
import base64
import json
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import psutil
from ultralytics import YOLO
import os
import picamera2

# Custom modules – pretpostavljamo da su dostupni u projektu
from src.utils.messages.allMessages import (
    mainCamera,
    serialCamera,
    Recording,
    Record,
    Brightness,
    Contrast,
)

from src.utils.messages.messageHandlerSender import messageHandlerSender
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.templates.threadwithstop import ThreadWithStop

# Dobijamo direktorijum u kojem se nalazi trenutna skripta
script_dir = os.path.dirname(os.path.abspath(__file__))
# Kreiramo apsolutnu putanju do modela koji se nalazi u istom folderu
model_path_yolo = os.path.join(script_dir, "best.pt")


# --- FrameBuffer definicija ---
class FrameBuffer:
    """Jednostavni buffer koji drži frame i timestamp preuzimanja."""
    def __init__(self):
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

# --- Klasa HoughTransformation ---
class HoughTransformation:
    """Klasa koja vrši obradu frameova koristeći Hough transformaciju."""
    def __init__(self, logger, gamma=1.2):
        self.logger = logger
        self.gamma = gamma

    def adjust_gamma(self, image, gamma=1.2):
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(image, table)

    def process_frame(self, frame):
        if frame is None:
            self.logger.error("Primljen main frame je None u HoughTransformation.")
            return None

        resized_frame = cv2.resize(frame, (1024, 540))
        height, width = resized_frame.shape[:2]

        roi_pts = np.array([
            [0, height],
            [width, height],
            [int(2 * width / 3), int(2 * height / 3)],
            [int(width / 3), int(2 * height / 3)]
        ], np.int32)
        roi_pts[:, 0] = np.clip(roi_pts[:, 0], 0, width - 1)
        roi_pts[:, 1] = np.clip(roi_pts[:, 1], 0, height - 1)
        x, y, w, h = cv2.boundingRect(roi_pts)
        if w == 0 or h == 0:
            self.logger.error("Degenerisana ROI oblast u HoughTransformation.")
            return resized_frame

        roi_img = resized_frame[y:y+h, x:x+w].copy()
        roi_pts_adjusted = roi_pts - [x, y]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [roi_pts_adjusted], 255)
        self.logger.debug(f"ROI shape: {roi_img.shape}, mask shape: {mask.shape}")
        try:
            roi_only = cv2.bitwise_and(roi_img, roi_img, mask=mask)
        except Exception as e:
            self.logger.error(f"cv2.bitwise_and greška u HoughTransformation: {e}")
            return resized_frame

        roi_gamma = self.adjust_gamma(roi_only, gamma=self.gamma)
        gray = cv2.cvtColor(roi_gamma, cv2.COLOR_BGR2GRAY)
        blurred = cv2.blur(gray, (3, 3))
        edges = cv2.Canny(blurred, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=20)
        roi_processed = np.copy(roi_img)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(roi_processed, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            self.logger.debug("Nije pronađena nijedna linija u ROI-ju za HoughTransformation.")

        roi_final = roi_img.copy()
        roi_final[mask == 255] = roi_processed[mask == 255]
        output_frame = np.copy(resized_frame)
        output_frame[y:y+h, x:x+w] = roi_final
        cv2.polylines(output_frame, [roi_pts], isClosed=True, color=(0, 0, 255), thickness=2)
        return output_frame

# --- Klasa ObjectDetectionThread za YOLO obradu ---
class ObjectDetectionThread(threading.Thread):
    def __init__(self, frame_buffer, queuesList, logger, parent, model_path=model_path_yolo):
        super(ObjectDetectionThread, self).__init__()
        self.frame_buffer = frame_buffer
        self.queuesList = queuesList
        self.logger = logger
        self.running = True
        self.parent = parent  # Reference to threadCamera instance (za pristup record_yolo)
        self.model = YOLO(model_path)
        self.cpu_core = 0
        self.set_cpu_affinity()

    def set_cpu_affinity(self):
        pid = os.getpid()
        p = psutil.Process(pid)
        p.cpu_affinity([self.cpu_core])
        p.nice(0)

    def detect_objects(self, frame):
        results = self.model(frame)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                detections.append((x1, y1, x2, y2, conf, cls))
        return detections

    def run(self):
        while self.running:
            if not self.frame_buffer.event.wait(timeout=0.01):
                continue
            frame, timestamp = self.frame_buffer.get()
            self.frame_buffer.clear()
            if frame is None:
                continue
            start_time = time.time()
            detections = self.detect_objects(frame)
            end_time = time.time()
            processing_time = end_time - start_time
            self.logger.info(f"YOLO processing time: {processing_time:.3f}s, Detections: {len(detections)}")
            # Crtanje bounding box-ova
            for x1, y1, x2, y2, conf, cls in detections:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"{cls} {conf:.2f}", (int(x1), int(y1)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # Kodiranje slike u JPEG format i kreiranje JSON payloada
            _, encodedImg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            encodedImageData = base64.b64encode(encodedImg).decode("utf-8")
            payload = json.dumps({"parity": "even", "image": encodedImageData})
            self.queuesList.setdefault("yolo_output", threading.Queue()).put(payload)
            # Ako je snimanje YOLO izlaza aktivno, snimi frejm u video
            if self.parent.recording and self.parent.record_yolo:
                if self.parent.yolo_video_writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    filename = "yolo_output_" + str(time.time()) + ".avi"
                    self.logger.info(f"Starting YOLO recording with filename {filename}")
                    self.parent.yolo_video_writer = cv2.VideoWriter(filename, fourcc, self.parent.frame_rate, (1024, 540))
                self.parent.yolo_video_writer.write(frame)

    def stop(self):
        self.running = False

# --- Glavna klasa threadCamera ---
class threadCamera(ThreadWithStop):
    def __init__(self, queuesList, logger, debugger):
        super(threadCamera, self).__init__()
        self.queuesList = queuesList
        self.logger = logger if logger is not None else self._dummy_logger()
        self.debugger = debugger
        self.frame_rate = 16  # 16 fps
        self.recording = False
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.recordingSender = messageHandlerSender(self.queuesList, Recording)
        self.mainCameraSender = messageHandlerSender(self.queuesList, mainCamera)
        self.serialCameraSender = messageHandlerSender(self.queuesList, serialCamera)

        self.subscribe()
        self._init_camera()
        self.Queue_Sending()
        self.Configs()

        # Inicijalizacija flegova za snimanje
        self.record_raw = False
        self.record_processed = False
        self.record_yolo = False

        # Video writer objekti (svaki za svoj režim)
        self.raw_video_writer = None
        self.processed_video_writer = None
        self.yolo_video_writer = None

        # Kreiranje dva frame buffera i brojača
        self.frame_buffer_even = FrameBuffer()
        self.frame_buffer_odd = FrameBuffer()
        self.frame_counter = 0

        # Pokretanje YOLO niti (radi obrade parnih frejmova)
        self.yolo_thread = ObjectDetectionThread(self.frame_buffer_even, self.queuesList, self.logger, parent=self)
        self.yolo_thread.start()

        # Instanciranje HoughTransformation i pokretanje niti za obradu neparnih frejmova
        self.hough_transform = HoughTransformation(self.logger, gamma=1.2)
        self.hough_thread = threading.Thread(target=self.processing_loop_odd, name="HoughProcessing")
        self.hough_thread.start()

        self._acquisition_running = threading.Event()
        self._acquisition_running.set()
        self._processing_running = threading.Event()
        self._processing_running.set()

    def _dummy_logger(self):
        import logging
        logging.basicConfig(level=logging.DEBUG)
        return logging.getLogger("DummyLogger")

    def subscribe(self):
        self.recordSubscriber = messageHandlerSubscriber(self.queuesList, Record, "lastOnly", True)
        self.brightnessSubscriber = messageHandlerSubscriber(self.queuesList, Brightness, "lastOnly", True)
        self.contrastSubscriber = messageHandlerSubscriber(self.queuesList, Contrast, "lastOnly", True)

    def Queue_Sending(self):
        self.recordingSender.send(self.recording)
        threading.Timer(1, self.Queue_Sending).start()

    def Configs(self):
        if self.brightnessSubscriber.isDataInPipe():
            message = self.brightnessSubscriber.receive()
            if self.debugger:
                self.logger.info(f"Brightness poruka: {message}")
            self.camera.set_controls({
                "AeEnable": False,
                "AwbEnable": False,
                "Brightness": max(0.0, min(1.0, float(message))),
            })
        if self.contrastSubscriber.isDataInPipe():
            message = self.contrastSubscriber.receive()
            if self.debugger:
                self.logger.info(f"Contrast poruka: {message}")
            self.camera.set_controls({
                "AeEnable": False,
                "AwbEnable": False,
                "Contrast": max(0.0, min(32.0, float(message))),
            })
        threading.Timer(1, self.Configs).start()

    def capture_loop(self):
        while self._running and self._acquisition_running.is_set():
            try:
                frame = self.camera.capture_array("main", wait=True)
                if frame is not None:
                    self.frame_counter += 1
                    if self.frame_counter >= 16:
                        self.frame_counter = 1
                    # Podela frejmova: parni idu u buffer za YOLO, neparni u buffer za Hough obradu
                    if self.frame_counter % 2 == 0:
                        self.frame_buffer_even.update(frame)
                    else:
                        self.frame_buffer_odd.update(frame)
                    # Ako je aktivno snimanje raw frejmova, snimaj ulazni frame (resize-ovan)
                    if self.recording and self.record_raw:
                        if self.raw_video_writer is None:
                            fourcc = cv2.VideoWriter_fourcc(*"XVID")
                            filename = "raw_output_" + str(time.time()) + ".avi"
                            self.logger.info(f"Starting raw recording with filename {filename}")
                            self.raw_video_writer = cv2.VideoWriter(filename, fourcc, self.frame_rate, (1024, 540))
                        self.raw_video_writer.write(cv2.resize(frame, (1024, 540)))
                else:
                    self.logger.error("Capture loop: frame je None.")
            except Exception as e:
                self.logger.error(f"Capture loop error: {e}")
            time.sleep(0.001)

    def processing_loop_odd(self):
        while self._running and self._processing_running.is_set():
            if not self.frame_buffer_odd.event.wait(timeout=0.005):
                continue
            frame, capture_time = self.frame_buffer_odd.get()
            self.frame_buffer_odd.clear()
            if frame is None:
                continue
            proc_start = time.time()
            processed_frame = self.hough_transform.process_frame(frame)
            proc_end = time.time()
            self.logger.info(f"Hough processing delay: {(proc_end - capture_time):.3f}s")
            # Ako je aktivno snimanje obrađenih frejmova (Hough), snimi obrađeni frame
            if self.recording and self.record_processed:
                if self.processed_video_writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    filename = "processed_output_" + str(time.time()) + ".avi"
                    self.logger.info(f"Starting processed recording with filename {filename}")
                    self.processed_video_writer = cv2.VideoWriter(filename, fourcc, self.frame_rate, (1024, 540))
                self.processed_video_writer.write(processed_frame)
            _, encodedImg = cv2.imencode(".jpg", processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            encodedImageData = base64.b64encode(encodedImg).decode("utf-8")
            payload = json.dumps({"parity": "odd", "image": encodedImageData})
            self.queuesList.setdefault("hough_output", threading.Queue()).put(payload)

    def run(self):
        self.capture_thread = threading.Thread(target=self.capture_loop, name="CameraCapture")
        self.capture_thread.start()
        while self._running:
            time.sleep(0.1)
        self._acquisition_running.clear()
        self._processing_running.clear()
        self.capture_thread.join()
        self.hough_thread.join()

    def stop(self):
        if self.raw_video_writer is not None:
            self.raw_video_writer.release()
        if self.processed_video_writer is not None:
            self.processed_video_writer.release()
        if self.yolo_video_writer is not None:
            self.yolo_video_writer.release()
        super(threadCamera, self).stop()
        if self.yolo_thread is not None:
            self.yolo_thread.stop()
            self.yolo_thread.join()
        if self.hough_thread is not None:
            self.hough_thread.join()

    def _init_camera(self):
        self.camera = picamera2.Picamera2()
        config = self.camera.create_preview_configuration(
            buffer_count=1,
            queue=False,
            main={"format": "RGB888", "size": (2048, 1080)},
            lores={"format": "YUV420", "size": (512, 270)}
        )
        self.camera.configure(config)
        self.camera.start()
        time.sleep(2)

if __name__ == "__main__":
    cam = threadCamera({}, None, True)
    # Omogućite snimanje tako što postavite odgovarajuće flegove:
    # cam.record_raw = True
    # cam.record_processed = True
    # cam.record_yolo = True
    while True:
        if "yolo_output" in cam.queuesList and not cam.queuesList["yolo_output"].empty():
            yolo_payload = cam.queuesList["yolo_output"].get()
            data = json.loads(yolo_payload)
            encoded_image = data.get("image", "")
            if encoded_image:
                decoded_image = base64.b64decode(encoded_image)
                np_arr = np.frombuffer(decoded_image, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                cv2.imshow("YOLO Output", frame)
        if "hough_output" in cam.queuesList and not cam.queuesList["hough_output"].empty():
            hough_payload = cam.queuesList["hough_output"].get()
            data = json.loads(hough_payload)
            encoded_image = data.get("image", "")
            if encoded_image:
                decoded_image = base64.b64decode(encoded_image)
                np_arr = np.frombuffer(decoded_image, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                cv2.imshow("Hough Output", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.stop()
    cv2.destroyAllWindows()
