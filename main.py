#!/usr/bin/env python3
import time
import logging
from utils.logger import get_logger
import config.config as cfg_module

from firmware.nucleo_comm import NucleoComm
from firmware.sensor_manager import SensorManager
from firmware.motor_control import MotorControl

from apis.bosch_api import BoschAPI
from apis.simulated_server import SimulatedServer

from utils.parallel import run_in_thread
from monitoring.monitor import Monitor, DashboardServer

def main():
    logger = get_logger('Main')
    logger.info("Pokretanje Brain sistema...")

    try:
        config_data = cfg_module.load_config()
    except Exception as e:
        logger.error("Greška pri učitavanju konfiguracije: %s", e)
        return

    try:
        nucleo = NucleoComm(config_data.get("nucleo", {}))
        sensor_manager = SensorManager(config_data.get("sensors", {}))
        motor_control = MotorControl(config_data.get("motors", {}))
    except Exception as e:
        logger.error("Greška pri inicijalizaciji hardvera: %s", e)
        return

    try:
        bosch_api = BoschAPI(config_data.get("apis", {}).get("bosch", {}))
        simulated_server = SimulatedServer(config_data.get("apis", {}).get("simulated", {}))
    except Exception as e:
        logger.error("Greška pri inicijalizaciji API-ja: %s", e)
        return

    # Pokrećemo akviziciju senzorskih podataka u zasebnoj niti
    sensor_thread = run_in_thread(
        target=sensor_manager.start_acquisition,
        name="SensorThread"
    )

    # Pokrećemo monitoring sistema (koji uključuje dashboard i endpoint za kontrolu)
    monitor_instance = Monitor(sensor_manager, motor_control, nucleo, config_data.get("monitor_interval", 1.0))
    monitor_instance.start()

    # Ako je dashboard omogućen, pokrećemo ga
    if config_data.get("dashboard_enabled", False):
        dashboard_host = config_data.get("dashboard_host", "0.0.0.0")
        dashboard_port = config_data.get("dashboard_port", 124)
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

if __name__ == "__main__":
    main()
