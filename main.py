#!/usr/bin/env python3
import time
from multiprocessing import Queue, Event
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

# Zastavice za pokretanje procesa
DASHBOARD = True
CAMERA = True
SERIAL_HANDLER = True

# Kreiramo međuprocesne queue-e
queueList = {
    "Critical": Queue(),
    "Warning": Queue(),
    "General": Queue(),  # Ovaj queue se koristi za tastaturu i telemetriju
    "Config": Queue(),
}

allProcesses = []

# ---------------------- Gateway proces ----------------------
from firmware.processGateway import processGateway
gatewayProc = processGateway(queueList, logger)
gatewayProc.start()
logger.info("Gateway proces pokrenut.")

# ---------------------- Zamena IP adrese ----------------------
from utils.ipManager.IpReplacement import IPManager
# Ako fajl ne postoji, ovaj modul će ispisati upozorenje.
ipChanger = IPManager('./utils/ipManager/web-socket.service.ts')
ipChanger.replace_ip_in_file()

# ---------------------- Dashboard proces ----------------------
if DASHBOARD:
    from frontend.processDashboard import processDashboard
    dashboardProc = processDashboard(queueList, logger, debugging=False)
    allProcesses.append(dashboardProc)

# ---------------------- Kamera proces ----------------------
if CAMERA:
    from camera.processCamera import processCamera
    cameraProc = processCamera(queueList, logger, debugging=False)
    allProcesses.append(cameraProc)

# ---------------------- SerialHandler proces ----------------------
if SERIAL_HANDLER:
    from firmware.processSerialHandler import processSerialHandler
    serialProc = processSerialHandler(queueList, logger, debugging=False)
    allProcesses.append(serialProc)

# ---------------------- Tastatura proces ----------------------

# Pokrećemo sve procese; WorkerProcess klase već postavljaju daemon u __init__
for proc in allProcesses:
    proc.start()

time.sleep(1)
print("""
---------------------------------
   BFMC SYSTEM – Vozilo spremno!
   (Pritisni Ctrl+C za prekid)
---------------------------------
""")

blocker = Event()
try:
    blocker.wait()
except KeyboardInterrupt:
    print("\nPrekid (Ctrl+C). Zaustavljam procese...")
    for proc in reversed(allProcesses):
        if hasattr(proc, 'stop'):
            proc.stop()
        logger.info("Proces zaustavljen: %s", proc)
    if hasattr(gatewayProc, 'stop'):
        gatewayProc.stop()
    print("Gateway proces zaustavljen.")
