import logging
import time
from multiprocessing import Process
from config import config
from firmware.nucleo_comm import NucleoComm
from firmware.motor_control import MotorControl
from firmware.sensor_manager import SensorManager
from monitoring.monitor import Monitor, DashboardServer

def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    logger = logging.getLogger("Main")
    logger.info("Pokretanje Brain sistema...")

    config_data = config.load_config()

    # Start separate camera process pinned to a specific core (e.g., core 3)
    from firmware.camera_process import camera_process  # assume you put the above function in camera_process.py
    cam_proc = Process(target=camera_process, args=(config_data, 3))
    cam_proc.start()

    # Initialize other components as before
    nucleo = NucleoComm(config_data.get("nucleo", {}))
    motor_control = MotorControl(config_data.get("motors", {}), nucleo_comm=nucleo)
    sensor_manager = SensorManager(config_data.get("sensors", {}))
    monitor_instance = Monitor(sensor_manager, motor_control, nucleo, config_data.get("monitor_interval", 1.0))
    monitor_instance.start()

    if config_data.get("dashboard_enabled", False):
        dashboard_host = config_data.get("dashboard_host", "0.0.0.0")
        dashboard_port = config_data.get("dashboard_port", 5000)
        dashboard = DashboardServer(monitor_instance, host=dashboard_host, port=dashboard_port)
        dashboard.start()
        logger.info("Dashboard integracija je omogućena.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Prekid od strane korisnika. Gašenje sistema...")
    finally:
        sensor_manager.stop_acquisition()
        monitor_instance.stop()
        cam_proc.terminate()
        cam_proc.join()

if __name__ == "__main__":
    main()
