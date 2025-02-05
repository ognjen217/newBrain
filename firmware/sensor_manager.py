import time
import cv2
import base64
import logging
from picamera2 import Picamera2

class SensorManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("SensorManager")
        self.picam2 = None
        self.initialize_camera()

    def initialize_camera(self):
        try:
            self.picam2 = Picamera2()
            # Create a still configuration at 640x480 resolution (adjust as needed)
            still_config = self.picam2.create_still_configuration(main={"size": (640, 480)})
            self.picam2.configure(still_config)
            self.picam2.start()
            time.sleep(2)  # Allow time for the camera to warm up
            self.logger.info("Picamera2 initialized successfully.")
        except Exception as e:
            self.logger.error("Error initializing Picamera2: %s", e)
            self.picam2 = None

    def capture_image(self):
        if self.picam2 is None:
            self.logger.error("Picamera2 is not initialized.")
            return None
        try:
            # Capture the image as a numpy array
            image = self.picam2.capture_array()
            # Convert BGR to RGB if necessary (adjust if your image is already in the right order)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Encode image as JPEG
            ret, jpeg = cv2.imencode('.jpg', image_rgb)
            if not ret:
                self.logger.error("Failed to encode image.")
                return None
            # Convert the JPEG to a Base64 string
            encoded = base64.b64encode(jpeg).decode('utf-8')
            return encoded
        except Exception as e:
            self.logger.error("Error capturing image: %s", e)
            return None

    def get_latest_data(self):
        # Get a current image (or you might cache and update this at a fixed interval)
        image = self.capture_image()
        # Return all sensor data in a dictionary (adjust as needed)
        return {
            "acceleration": [0, 0, 0],
            "gyro": [0, 0, 0],
            "speed": 0,
            "steering": 0,
            "battery_voltage": 0,
            "image": "printed"
        }
