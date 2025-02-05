import io
import base64
import logging
import time
import threading
import cv2
from picamera2 import Picamera2

class SensorManager:
    def __init__(self, config):
        """
        Initialize the SensorManager with the given configuration.
        :param config: Dictionary with configuration parameters.
        """
        self.config = config
        self.logger = logging.getLogger("SensorManager")
        self.acquisition_running = False
        self.data_lock = threading.Lock()
        self.latest_data = {
            "acceleration": [0, 0, 0],
            "gyro": [0, 0, 0],
            "speed": 0,
            "steering": 0,
            "battery_voltage": 0,
            "image": None
        }
        self.logger.info("SensorManager initialized with config: %s", config)
        self._init_camera()

    def _init_camera(self):
        """
        Initializes the Picamera2 instance for continuous use.
        """
        try:
            self.picam2 = Picamera2()
            still_config = self.picam2.create_still_configuration(main={"size": (640, 480)})
            self.picam2.configure(still_config)
            self.picam2.start()
            # Wait a bit longer to ensure the camera is fully ready
            time.sleep(5)
            self.logger.info("Picamera2 initialized successfully.")
        except Exception as e:
            self.logger.error("Error initializing Picamera2: %s", e)
            self.picam2 = None

    def _capture_image(self):
        """
        Captures an image using the pre-initialized Picamera2 instance.
        Converts the image from BGR to RGB, encodes it as JPEG and then Base64.
        :return: Base64 encoded JPEG image as a string, or None if an error occurs.
        """
        if self.picam2 is None:
            self.logger.error("Picamera2 instance is not initialized.")
            return None
        try:
            image = self.picam2.capture_array()
            # Convert from BGR to RGB (if needed)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            success, encoded_image = cv2.imencode('.jpg', image_rgb)
            if not success:
                self.logger.error("Failed to encode image")
                return None
            image_data = base64.b64encode(encoded_image).decode('utf-8')
            return image_data
        except Exception as e:
            self.logger.error("Error capturing image with Picamera2: %s", e)
            return None

    def _read_sensors(self):
        """
        Reads sensor data (IMU, speed, camera image, etc.) and returns a dictionary.
        :return: Dictionary of sensor data.
        """
        imu_data = {"acceleration": [0, 0, 0], "gyro": [0, 0, 0]}
        speed_data = {"speed": 0}
        image_data = self._capture_image()
        with self.data_lock:
            steering = self.latest_data.get("steering", 0)
            battery = self.latest_data.get("battery_voltage", 0)
        sensor_data = {**imu_data, **speed_data,
                       "image": image_data,
                       "steering": steering,
                       "battery_voltage": battery}
        self.logger.debug("Read sensor data: %s", sensor_data)
        return sensor_data

    def start_acquisition(self):
        """
        Starts continuous sensor data acquisition (to be run in a separate thread).
        """
        self.acquisition_running = True
        self.logger.info("Starting sensor acquisition.")
        while self.acquisition_running:
            sensor_data = self._read_sensors()
            with self.data_lock:
                self.latest_data.update(sensor_data)
            time.sleep(self.config.get("acquisition_interval", 0.1))

    def get_latest_data(self):
        """
        Returns the latest acquired sensor data.
        :return: A copy of the sensor data dictionary.
        """
        with self.data_lock:
            return self.latest_data.copy()

    def stop_acquisition(self):
        """
        Stops sensor data acquisition.
        """
        self.acquisition_running = False
        self.logger.info("Stopping sensor acquisition.")

    def update_steering(self, delta):
        """
        Updates the steering value.
        :param delta: Change in steering (negative for left, positive for right).
        """
        with self.data_lock:
            current = self.latest_data.get("steering", 0)
            new_value = current + delta
            self.latest_data["steering"] = new_value
        self.logger.info("Steering updated: %s -> %s", current, new_value)
