#!/usr/bin/env python3
import logging
import base64
import cv2
import time
from firmware.sensor_manager import SensorManager
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("TestCamera")

config_data = config.load_config()
sensor_manager = SensorManager(config_data.get("sensors", {}))

logger.info("Capturing an image using Picamera2...")
image_data = sensor_manager._capture_image()

if image_data:
    logger.info("Image captured successfully, length: %d", len(image_data))
    # Decode and save the image for inspection
    try:
        image_bytes = base64.b64decode(image_data)
        with open("test_image.jpg", "wb") as f:
            f.write(image_bytes)
        logger.info("Saved test_image.jpg")
    except Exception as e:
        logger.error("Error saving image: %s", e)
else:
    logger.error("Failed to capture image.")
