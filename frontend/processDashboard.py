from multiprocessing import Process
import threading
import time
import os
import logging
from flask import Flask, send_from_directory, jsonify, request

class processDashboard(Process):
    def __init__(self, queueList, logger, debugging=False):
        super(processDashboard, self).__init__()
        self.queueList = queueList
        self.logger = logger
        self.debugging = debugging
        self._running = True

    def run(self):
        # Postavimo static_folder na "front" unutar newBrain/frontend
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "front")
        app = Flask(__name__, static_folder=base_dir)
        telemetry_data = {
            "motorSpeed": "-",
            "steeringAngle": "-",
            "command": "-"
        }

        @app.route('/telemetry', methods=['GET'])
        def telemetry():
            return jsonify(telemetry_data)

        # Dodajemo novi endpoint za manual control:
        @app.route('/manual-control', methods=['POST'])
        def manual_control():
            data = request.get_json()
            key = data.get("key")
            if key and key.lower() in ['w', 'a', 's', 'd']:
                # Ubaci poruku u shared queue
                self.queueList["General"].put({"source": "keyboard", "command": key.lower()})
                return jsonify({"status": "ok", "key": key.lower()})
            else:
                return jsonify({"status": "error", "message": "Invalid key"}), 400

        @app.route('/<path:filename>')
        def serve_file(filename):
            return send_from_directory(app.static_folder, filename)

        @app.route('/')
        def index():
            return send_from_directory(app.static_folder, 'index.html')

        def update_telemetry():
            while self._running:
                if not self.queueList["General"].empty():
                    msg = self.queueList["General"].get()
                    if msg.get("source") in ["serial", "keyboard", "camera"]:
                        telemetry_data["command"] = msg.get("command", telemetry_data["command"])
                        telemetry_data["motorSpeed"] = msg.get("motorSpeed", telemetry_data["motorSpeed"])
                        telemetry_data["steeringAngle"] = msg.get("steeringAngle", telemetry_data["steeringAngle"])
                time.sleep(0.5)

        telemetry_thread = threading.Thread(target=update_telemetry)
        telemetry_thread.daemon = True
        telemetry_thread.start()

        self.logger.info("Dashboard pokrenut na portu 5000.")
        flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
        flask_thread.daemon = True
        flask_thread.start()

        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("Dashboard")
    processDashboard({}, logger).run()
