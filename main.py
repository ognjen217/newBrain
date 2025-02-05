#!/usr/bin/env python3
import time
import logging
from config import config
from firmware.nucleo_comm import NucleoComm
from firmware.motor_control import MotorControl
from firmware.sensor_manager import SensorManager
from monitoring.monitor import Monitor, DashboardServer

def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    logger = logging.getLogger("Main")
    logger.info("Starting Brain system...")

    config_data = config.load_config()

    # Instantiate Nucleo communication using the correct serial port
    nucleo = NucleoComm(config_data.get("nucleo", {}))
    
    # Create MotorControl with the NucleoComm instance
    motor_control = MotorControl(config_data.get("motors", {}), nucleo_comm=nucleo)
    
    # Initialize SensorManager (for camera and other sensor data)
    sensor_manager = SensorManager(config_data.get("sensors", {}))
    
    # Create and start the Monitor (for status and dashboard)
    monitor_instance = Monitor(sensor_manager, motor_control, nucleo, config_data.get("monitor_interval", 1.0))
    monitor_instance.start()

    if config_data.get("dashboard_enabled", False):
        dashboard_host = config_data.get("dashboard_host", "0.0.0.0")
        dashboard_port = config_data.get("dashboard_port", 5000)
        dashboard = DashboardServer(monitor_instance, host=dashboard_host, port=dashboard_port)
        dashboard.start()
        logger.info("Dashboard integration enabled.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        sensor_manager.stop_acquisition()
        monitor_instance.stop()

if __name__ == "__main__":
    main()
