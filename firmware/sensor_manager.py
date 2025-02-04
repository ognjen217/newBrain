import logging
import time
import threading

class SensorManager:
    def __init__(self, config):
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
        self.logger.info("SensorManager inicijalizovan sa konfiguracijom: %s", config)

    def start_acquisition(self):
        self.acquisition_running = True
        self.logger.info("Početak akvizicije senzorskih podataka.")
        while self.acquisition_running:
            sensor_data = self._read_sensors()
            with self.data_lock:
                self.latest_data.update(sensor_data)
            time.sleep(self.config.get("acquisition_interval", 0.1))

    def _read_sensors(self):
        imu_data = {"acceleration": [0, 0, 0], "gyro": [0, 0, 0]}
        camera_data = {"image": None}
        speed_data = {"speed": 0}
        with self.data_lock:
            steering = self.latest_data.get("steering", 0)
            battery = self.latest_data.get("battery_voltage", 0)
        sensor_data = {**imu_data, **camera_data, **speed_data,
                       "steering": steering, "battery_voltage": battery}
        self.logger.debug("Pročitani senzorski podaci: %s", sensor_data)
        return sensor_data

    def get_latest_data(self):
        with self.data_lock:
            return self.latest_data.copy()

    def stop_acquisition(self):
        self.acquisition_running = False
        self.logger.info("Zaustavljanje akvizicije senzorskih podataka.")

    def update_steering(self, delta):
        with self.data_lock:
            current = self.latest_data.get("steering", 0)
            new_value = current + delta
            self.latest_data["steering"] = new_value
        self.logger.info("Steering ažuriran: %s -> %s", current, new_value)
