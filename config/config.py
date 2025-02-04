"""
config/config.py - Centralizovani konfiguracioni fajl za Brain projekat.

Ovaj fajl sadrži sve globalne konfiguracione parametre kao rečnik i metodu load_config()
koja vraća konfiguraciju. Ukoliko se postavi varijabla okruženja BRAIN_CONFIG_PATH i postoji
JSON fajl na toj putanji, konfiguracija će biti učitana iz tog fajla, inače se koristi podrazumevana konfiguracija.
"""

import os
import json

# Podrazumevana konfiguracija
CONFIG = {
    "sensors": {
        "acquisition_interval": 0.1,
        # Parametri za kameru
        "camera_resolution": [640, 480],
        "camera_fps": 30,
        # Parametri za IMU (kalibracija)
        "imu_calibration": {
            "accel_offset": [0, 0, 0],
            "gyro_offset": [0, 0, 0]
        }
    },
    "motors": {
        "max_speed": 10,
        "min_speed": 0,
        "acceleration_step": 1,
        "deceleration_step": 1,
        "default_speed": 5
    },
    "nucleo": {
        "port": "/dev/ttyUSB0",
        "baudrate": 115200
    },
    "apis": {
        "bosch": {
            "endpoint": "https://bosch.example.com/api",
            "api_key": "YOUR_API_KEY",
            "timeout": 5
        },
        "simulated": {
            "delay": 0.5,
            "success_rate": 0.9
        }
    },
    "monitor_interval": 1.0,
    "dashboard_enabled": True,
    "dashboard_host": "0.0.0.0",
    "dashboard_port": 5000
}

def load_config():
    """
    Vraća konfiguraciju kao rečnik.
    
    Ako je postavljena varijabla okruženja 'BRAIN_CONFIG_PATH' i fajl postoji, učitava konfiguraciju iz JSON fajla.
    U suprotnom, vraća podrazumevane vrednosti.
    
    :return: Konfiguracioni rečnik
    """
    config_path = os.getenv("BRAIN_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return config_data
        except Exception as e:
            print(f"Greška pri učitavanju konfiguracije iz {config_path}: {e}")
    return CONFIG
