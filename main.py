#!/usr/bin/env python3
"""
Glavni ulazni fajl za Brain projekat.
Ovaj fajl inicijalizuje konfiguraciju, hardverske module i API-je, 
pokreće paralelnu akviziciju podataka sa senzora i sadrži osnovnu
kontrolnu petlju za upravljanje kretanjem robota.
"""

import time

# Uvoz centralizovanog sistema za logovanje
from utils.logger import get_logger

# Uvoz konfiguracije (pretpostavlja se da postoji load_config() koja vraća rečnik)
import config.config as cfg_module

# Uvoz hardverskih modula
from firmware.nucleo_comm import NucleoComm
from firmware.sensor_manager import SensorManager
from firmware.motor_control import MotorControl

# Uvoz API modula
from apis.bosch_api import BoschAPI
from apis.simulated_server import SimulatedServer

# Uvoz modula za paralelizaciju – ovde se pretpostavlja enkapsulacija Python-ovog threading modula
import utils.parallel as parallel


def main():
    logger = get_logger('Main')
    logger.info("Pokretanje Brain sistema...")

    # Učitavanje konfiguracionih parametara
    try:
        config = cfg_module.load_config()
    except Exception as e:
        logger.error("Greška pri učitavanju konfiguracije: %s", e)
        return

    # Inicijalizacija hardverskih modula
    try:
        nucleo = NucleoComm(config.get("nucleo", {}))
        sensor_manager = SensorManager(config.get("sensors", {}))
        motor_control = MotorControl(config.get("motors", {}))
    except Exception as e:
        logger.error("Greška pri inicijalizaciji hardvera: %s", e)
        return

    # Inicijalizacija API modula
    try:
        bosch_api = BoschAPI(config.get("bosch", {}))
        simulated_server = SimulatedServer(config.get("simulated", {}))
    except Exception as e:
        logger.error("Greška pri inicijalizaciji API-ja: %s", e)
        return

    # Pokretanje akvizicije senzorskih podataka u zasebnoj niti/ procesu
    sensor_thread = parallel.Thread(
        target=sensor_manager.start_acquisition,
        name="SensorThread"
    )
    sensor_thread.start()

    logger.info("Inicijalizacija završena. Ulazak u glavnu petlju.")

    try:
        # Glavna kontrolna petlja – prilagodite logiku po potrebi
        while True:
            # Preuzimanje najnovijih podataka sa senzora
            sensor_data = sensor_manager.get_latest_data()
            logger.debug("Podaci sa senzora: %s", sensor_data)

            # Slanje podataka na Bosch API (ili pokretanje neke analize)
            api_response = bosch_api.send_data(sensor_data)
            logger.debug("Odgovor Bosch API-ja: %s", api_response)

            # Primer jednostavne logike: regulacija brzine na osnovu senzorskih podataka
            desired_speed = config.get("desired_speed", 5)
            current_speed = sensor_data.get("speed", 0)
            if current_speed < desired_speed:
                motor_control.accelerate()
                logger.debug("Povećavam brzinu.")
            elif current_speed > desired_speed:
                motor_control.decelerate()
                logger.debug("Smanjujem brzinu.")
            else:
                motor_control.maintain_speed()
                logger.debug("Održavam brzinu.")

            # Pauza između iteracija glavne petlje
            time.sleep(config.get("loop_delay", 0.1))

    except KeyboardInterrupt:
        logger.info("Prekid od strane korisnika. Pokreće se ispravno gašenje sistema.")
    except Exception as e:
        logger.error("Izuzetak u glavnoj petlji: %s", e)
    finally:
        # Prekid akvizicije senzora i čekanje da se nit zaustavi
        sensor_manager.stop_acquisition()
        sensor_thread.join(timeout=2)
        logger.info("Gašenje Brain sistema završeno.")


if __name__ == "__main__":
    main()
