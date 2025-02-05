import os
import time
import logging
from firmware.sensor_manager import SensorManager
from config import config

def camera_process(config_data, core_id=3):
    # Postavi affinity za ovaj podproces
    try:
        os.sched_setaffinity(0, {core_id})
        print(f"Camera process pinned to core {core_id}")
    except Exception as e:
        print(f"Failed to set CPU affinity in camera process: {e}")

    logger = logging.getLogger("CameraProcess")
    sensor_manager = SensorManager(config_data.get("sensors", {}))
    while True:
        image = sensor_manager._capture_image()  # or sensor_manager._read_sensors() if you want more data
        # Ovde možete poslati image na neki kanal, sačuvati ga, ili ga proslediti (npr. putem IPC)
        logger.info("Captured an image")
        time.sleep(config_data.get("acquisition_interval", 0.1))
