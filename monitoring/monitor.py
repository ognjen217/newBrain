#!/usr/bin/env python3
"""
monitor.py - Modul za monitoring sistema u Brain projektu sa integracijom web dashboarda.
Ovaj modul pokreće monitoring petlju koja periodično prikuplja status sistema (senzori, motor, Nucleo, CPU)
i pokreće Flask web server sa sledećim endpoint-ima:
  - "/"          -> prikazuje dashboard (dashboard.html)
  - "/api/status"-> vraća status u JSON formatu
  - "/control"   -> prihvata POST zahteve sa komandom (W, A, S, D) za kontrolu
"""

import time
import threading
import logging
import os
import psutil
from flask import Flask, jsonify, render_template, request

# Monitor klasa: prikuplja status iz senzora, motora, Nucleo veze i CPU-a.
class Monitor:
    def __init__(self, sensor_manager, motor_control, nucleo_comm, monitor_interval=1.0):
        self.sensor_manager = sensor_manager
        self.motor_control = motor_control
        self.nucleo_comm = nucleo_comm
        self.monitor_interval = monitor_interval
        self.logger = logging.getLogger("Monitor")
        self.running = False

    def get_system_status(self):
        sensor_data = self.sensor_manager.get_latest_data() if self.sensor_manager else {}
        motor_status = {"current_speed": self.motor_control.current_speed} if self.motor_control else {}
        nucleo_status = self.nucleo_comm.connection if self.nucleo_comm else {}
        cpu_status = psutil.cpu_percent(interval=None, percpu=True)
        status = {
            "sensor_data": sensor_data,
            "motor_status": motor_status,
            "nucleo_status": nucleo_status,
            "cpu_status": cpu_status
        }
        return status

    def monitor_loop(self):
        self.logger.info("Monitoring petlja pokrenuta.")
        self.running = True
        while self.running:
            status = self.get_system_status()
            self.logger.info("Sistemski status: %s", status)
            time.sleep(self.monitor_interval)

    def start(self):
        self.monitor_thread = threading.Thread(target=self.monitor_loop, name="MonitorThread", daemon=True)
        self.monitor_thread.start()
        self.logger.info("Monitoring nit pokrenuta.")

    def stop(self):
        self.running = False
        self.monitor_thread.join(timeout=self.monitor_interval * 2)
        self.logger.info("Monitoring nit zaustavljena.")


# DashboardServer klasa: pokreće Flask web server s endpoint-ima za prikaz statusa i kontrolu.
class DashboardServer:
    def __init__(self, monitor, host='0.0.0.0', port=5000):
        # Odredite apsolutnu putanju do foldera "templates" (pretpostavlja se da se nalazi u korenu projekta)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_folder = os.path.join(current_dir, "..", "templates")
        self.app = Flask(__name__, template_folder=template_folder)
        self.monitor = monitor
        self.host = host
        self.port = port
        self._setup_routes()
        self.logger = logging.getLogger("DashboardServer")

    def _setup_routes(self):
        @self.app.route("/")
        def index():
            status = self.monitor.get_system_status()
            return render_template("dashboard.html", status=status)

        @self.app.route("/api/status")
        def api_status():
            status = self.monitor.get_system_status()
            return jsonify(status)

        @self.app.route("/control", methods=["POST"])
        def control():
            data = request.get_json()
            command = data.get("command")
            if not hasattr(self.monitor, "motor_control"):
                return jsonify({"status": "error", "message": "Motor kontrola nije dostupna"}), 500

            if command == "W":
                self.monitor.motor_control.accelerate()
            elif command == "S":
                self.monitor.motor_control.decelerate()
            elif command == "A":
                if hasattr(self.monitor.sensor_manager, "update_steering"):
                    self.monitor.sensor_manager.update_steering(-10)
            elif command == "D":
                if hasattr(self.monitor.sensor_manager, "update_steering"):
                    self.monitor.sensor_manager.update_steering(10)
            else:
                return jsonify({"status": "error", "message": "Nepoznata komanda"}), 400

            return jsonify({"status": "ok", "command": command})

    def start(self):
        def run_flask():
            self.logger.info("Dashboard server pokrenut na %s:%s", self.host, self.port)
            # use_reloader=False sprečava višestruko pokretanje niti
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        self.dashboard_thread = threading.Thread(target=run_flask, name="DashboardThread", daemon=True)
        self.dashboard_thread.start()


# Ako se ovaj modul pokreće direktno, pokreće se i main() funkcija za testiranje.
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    logger = logging.getLogger("MonitorMain")
    logger.info("Pokretanje monitoring sistema...")

    # Inicijalizacija modula: učitajte konfiguraciju i kreirajte instance senzorskog menadžera, motora i Nucleo komunikacije.
    from firmware.sensor_manager import SensorManager
    from firmware.motor_control import MotorControl
    from firmware.nucleo_comm import NucleoComm
    from config import config
    config_data = config.load_config()

    sensor_manager = SensorManager(config_data.get("sensors", {}))
    motor_control = MotorControl(config_data.get("motors", {}))
    nucleo_comm = NucleoComm(config_data.get("nucleo", {}))
    monitor_instance = Monitor(sensor_manager, motor_control, nucleo_comm, config_data.get("monitor_interval", 1.0))
    monitor_instance.start()

    # Pokrenite dashboard server ako je omogućen u konfiguraciji.
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
        logger.info("Prekid od strane korisnika. Zaustavljanje monitora...")
    finally:
        sensor_manager.stop_acquisition()
        monitor_instance.stop()

if __name__ == "__main__":
    main()
