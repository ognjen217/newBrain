#!/usr/bin/env python3
"""
monitor.py - Module for monitoring system status and serving a web dashboard.
Provides endpoints:
  - "/" to render the dashboard template,
  - "/api/status" to return sensor data,
  - "/control" to receive keyboard commands.
"""

import time
import threading
import logging
import os
import psutil
from flask import Flask, jsonify, render_template, request

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
        nucleo_status = {"status": "connected"} if (self.nucleo_comm and getattr(self.nucleo_comm, "connection", None)) else {"status": "disconnected"}
        cpu_status = psutil.cpu_percent(interval=None, percpu=True)
        status = {
            "sensor_data": sensor_data,
            "motor_status": motor_status,
            "nucleo_status": nucleo_status,
            "cpu_status": cpu_status
        }
        return status

    def log_system_status(self):
        status = self.get_system_status()
        # If sensor_data has a large "image" field, truncate it before logging
        sensor_data = status.get("sensor_data", {}).copy()
        image_str = sensor_data.get("image")
        if image_str and isinstance(image_str, str) and len(image_str)>550:
            sensor_data["image"] = image_str[:50] + "..."  # Only show the first 50 characters
        self.logger.info("System status: %s", {**status,"sensor_data":sensor_data})


    def monitor_loop(self):
        self.logger.info("Starting monitor loop.")
        self.running = True
        while self.running:
            status = self.get_system_status()
            self.log_system_status()
            time.sleep(self.monitor_interval)

    def start(self):
        self.monitor_thread = threading.Thread(target=self.monitor_loop, name="MonitorThread", daemon=True)
        self.monitor_thread.start()
        self.logger.info("Monitor thread started.")

    def stop(self):
        self.running = False
        self.monitor_thread.join(timeout=self.monitor_interval * 2)
        self.logger.info("Monitor thread stopped.")

class DashboardServer:
    def __init__(self, monitor, host='0.0.0.0', port=5000):
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
            self.logger.info("Received command: %s", command)
            if not hasattr(self.monitor, "motor_control"):
                return jsonify({"status": "error", "message": "Motor control unavailable"}), 500

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
                return jsonify({"status": "error", "message": "Unknown command"}), 400

            return jsonify({"status": "ok", "command": command})

    def start(self):
        def run_flask():
            self.logger.info("Dashboard server running on %s:%s", self.host, self.port)
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        self.dashboard_thread = threading.Thread(target=run_flask, name="DashboardThread", daemon=True)
        self.dashboard_thread.start()
