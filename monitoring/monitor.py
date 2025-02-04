#!/usr/bin/env python3
"""
monitor.py - Modul za monitoring performansi i stanja sistema u Brain projektu,
sa integracijom web dashboarda.

Ovaj modul:
  • Pokreće monitoring petlju koja periodično prikuplja status iz modula:
      - SensorManager (senzorski podaci, uključujući output kamere, steering i baterijski napon)
      - MotorControl (brzina motora)
      - NucleoComm (status komunikacije)
      - Psutil za stanje svih CPU core-ova
  • Ako je u konfiguraciji omogućeno, pokreće se i web dashboard (Flask server)
    koji omogućava pregled statusa sistema putem web interfejsa.
"""

import time
import threading
import logging
import psutil  # Biblioteka za prikupljanje podataka o procesorskim jezgrima

from flask import Flask, jsonify, render_template

# Učitavanje konfiguracije – očekuje se da config modul ima metodu load_config()
from config import config

# Uvoz modula iz firmware paketa
from firmware.sensor_manager import SensorManager
from firmware.motor_control import MotorControl
from firmware.nucleo_comm import NucleoComm


class Monitor:
    def __init__(self, sensor_manager, motor_control, nucleo_comm, monitor_interval=1.0):
        """
        Inicijalizacija monitora.
        :param sensor_manager: Instance klase SensorManager
        :param motor_control: Instance klase MotorControl
        :param nucleo_comm: Instance klase NucleoComm
        :param monitor_interval: Interval (u sekundama) između očitavanja statusa
        """
        self.sensor_manager = sensor_manager
        self.motor_control = motor_control
        self.nucleo_comm = nucleo_comm
        self.monitor_interval = monitor_interval
        self.logger = logging.getLogger("Monitor")
        self.running = False

    def get_system_status(self):
        """
        Prikuplja status sistema iz dostupnih modula i vraća ga kao rečnik.
        Očekuje se da sensor_manager.get_latest_data() vraća rečnik sa bar ovim ključevima:
          - "image": output sa kamere (npr. base64 enkodirana slika ili URL)
          - "steering": vrednost ugla upravljanja
          - "battery_voltage": stanje napona baterije
          - ostali senzorski podaci (npr. "acceleration", "gyro", "speed", …)
        MotorControl daje "current_speed", a putem psutil se dodaju podaci o CPU jezgrima.
        """
        sensor_data = self.sensor_manager.get_latest_data() if self.sensor_manager else {}
        motor_status = {"current_speed": self.motor_control.current_speed} if self.motor_control else {}
        nucleo_status = self.nucleo_comm.connection if self.nucleo_comm else {}
        cpu_status = psutil.cpu_percent(interval=None, percpu=True)  # Lista sa procentima po jezgru

        status = {
            "sensor_data": sensor_data,
            "motor_status": motor_status,
            "nucleo_status": nucleo_status,
            "cpu_status": cpu_status
        }
        return status

    def monitor_loop(self):
        """
        Glavna monitoring petlja – periodično prikuplja i loguje status sistema.
        """
        self.logger.info("Monitoring petlja pokrenuta.")
        self.running = True
        while self.running:
            status = self.get_system_status()
            self.logger.info("Sistemski status: %s", status)
            time.sleep(self.monitor_interval)

    def start(self):
        """
        Pokreće monitoring petlju u zasebnoj niti.
        """
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop, name="MonitorThread", daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Monitoring nit pokrenuta.")

    def stop(self):
        """
        Prekida monitoring petlju i čeka da se nit ispravno zaustavi.
        """
        self.running = False
        self.monitor_thread.join(timeout=self.monitor_interval * 2)
        self.logger.info("Monitoring nit zaustavljena.")


class DashboardServer:
    def __init__(self, monitor, host='0.0.0.0', port=5000):
        """
        Inicijalizacija Dashboard servera.
        :param monitor: Instance klase Monitor, korišćena za dohvat statusa sistema.
        :param host: Host adresa na kojoj će Flask server da sluša.
        :param port: Port na kojem će Flask server da sluša.
        """
        self.monitor = monitor
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self._setup_routes()
        self.logger = logging.getLogger("DashboardServer")

    def _setup_routes(self):
        """
        Definiše rute za dashboard.
        """
        @self.app.route("/")
        def index():
            status = self.monitor.get_system_status()
            # Renderovanje eksternog template-a dashboard.html iz direktorijuma templates/
            return render_template("dashboard.html", status=status)

        @self.app.route("/api/status")
        def api_status():
            status = self.monitor.get_system_status()
            return jsonify(status)

    def start(self):
        """
        Pokreće Flask server u zasebnoj niti.
        """
        def run_flask():
            self.logger.info("Dashboard server pokrenut na %s:%s", self.host, self.port)
            # use_reloader=False sprečava višestruko pokretanje niti
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

        self.dashboard_thread = threading.Thread(
            target=run_flask, name="DashboardThread", daemon=True
        )
        self.dashboard_thread.start()


def main():
    # Konfigurišemo osnovno logovanje
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    logger = logging.getLogger("MonitorMain")

    # Učitavanje konfiguracije
    try:
        cfg = config.load_config()
    except Exception as e:
        logger.error("Greška pri učitavanju konfiguracije: %s", e)
        return

    # Inicijalizacija modula iz firmware paketa
    try:
        sensor_manager = SensorManager(cfg.get("sensors", {}))
        motor_control = MotorControl(cfg.get("motors", {}))
        nucleo_comm = NucleoComm(cfg.get("nucleo", {}))
    except Exception as e:
        logger.error("Greška pri inicijalizaciji modula: %s", e)
        return

    monitor_interval = cfg.get("monitor_interval", 1.0)
    monitor = Monitor(sensor_manager, motor_control, nucleo_comm, monitor_interval)

    # Pokrećemo monitoring
    monitor.start()

    # Ako je u konfiguraciji omogućena integracija sa dashboardom, pokrećemo ga u zasebnoj niti
    if cfg.get("dashboard_enabled", False):
        dashboard_host = cfg.get("dashboard_host", "0.0.0.0")
        dashboard_port = cfg.get("dashboard_port", 5000)
        dashboard = DashboardServer(monitor, host=dashboard_host, port=dashboard_port)
        dashboard.start()
        logger.info("Dashboard integracija je omogućena.")

    # Glavna petlja – održavamo proces dok se ne prekine (Ctrl+C)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Prekid od strane korisnika. Zaustavljanje monitora...")
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
