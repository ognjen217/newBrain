import os
import json

# Default configuration
CONFIG = {
    "sensors": {
        "acquisition_interval": 0.1
    },
    "motors": {
        "max_speed": 10,
        "min_speed": 0,
        "acceleration_step": 1,
        "deceleration_step": 1
    },
    "nucleo": {
        "port": "/dev/ttyACM0",  # Change to the correct serial port (e.g., /dev/ttyUSB0 or /dev/ttyACM0)
        "baudrate": 115200
    },
    "monitor_interval": 1.0,
    "dashboard_enabled": True,
    "dashboard_host": "0.0.0.0",
    "dashboard_port": 5000
}

def load_config():
    config_path = os.getenv("BRAIN_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return config_data
        except Exception as e:
            print(f"Greška pri učitavanju konfiguracije iz {config_path}: {e}")
    return CONFIG
