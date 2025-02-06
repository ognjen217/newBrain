# app.py
import logging
from flask import Flask, request, jsonify, render_template
from firmware.nucleo_comm import NucleoComm

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Konfiguracija – prilagodi port ako je potrebno
nucleo_config = {
    "port": "/dev/ttyACM0",
    "baudrate": 115200
}

# Inicijaliziraj NucleoComm
nucleo_comm = NucleoComm(nucleo_config)

@app.route('/')
def index():
    # Renderiraj dashboard – koristiš templates/dashboard.html
    return render_template('dashboard.html')

@app.route('/sendKey', methods=['POST'])
def send_key():
    data = request.get_json()
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "Key nije poslan"}), 400
    try:
        nucleo_comm.send_key_command(key)
        return jsonify({"status": "ok", "key": key})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/setKlValue', methods=['POST'])
def set_kl_value():
    data = request.get_json()
    try:
        kl_value = int(data.get("kl_value", 0))
    except ValueError:
        return jsonify({"status": "error", "message": "KL vrijednost mora biti broj"}), 400
    try:
        nucleo_comm.send_kl_command(kl_value)
        return jsonify({"status": "ok", "kl_value": kl_value})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
