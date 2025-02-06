# app.py
import logging
from flask import Flask, request, jsonify, render_template
from firmware.nucleo_comm import NucleoComm

# Postavi osnovnu konfiguraciju za logiranje (opcionalno, ali korisno za debug)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Konfiguracija za serijski port – prilagodi prema svom okruženju
nucleo_config = {
    "port": "/dev/ttyACM0",   # Promijeni ako je potrebno (npr. /dev/ttyAMA0)
    "baudrate": 115200
}

# Inicijaliziraj instancu NucleoComm (koja koristi firmware/nucleo_comm.py)
nucleo_comm = NucleoComm(nucleo_config)

@app.route('/')
def index():
    """
    Glavna stranica – prikazuje dashboard.
    Preporučujem da se ne dira postojeći video feed ako već radi,
    te se dodatno prikažu tipke i slider za komande.
    """
    return render_template('dashboard.html')

@app.route('/sendKey', methods=['POST'])
def send_key():
    """
    Endpoint koji prima JSON sa ključem "key" (npr. "W", "A", "S", "D").
    Poziva metodu send_key_command iz NucleoComm.
    """
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
    """
    Endpoint koji prima JSON sa ključem "kl_value" (npr. "0", "15" ili "30").
    Poziva metodu send_kl_command iz NucleoComm.
    """
    data = request.get_json()
    try:
        kl_value = int(data.get("kl_value", 0))
    except ValueError:
        return jsonify({"status": "error", "message": "Kl vrijednost mora biti broj"}), 400

    try:
        nucleo_comm.send_kl_command(kl_value)
        return jsonify({"status": "ok", "kl_value": kl_value})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Pokreće Flask server; debug=True je koristan za razvoj
    app.run(debug=True, host='0.0.0.0')
