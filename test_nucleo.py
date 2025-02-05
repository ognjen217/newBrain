import logging
from firmware.nucleo_comm import NucleoComm
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("TestNucleo")
config_data = config.load_config()
nucleo = NucleoComm(config_data.get("nucleo", {}))
if nucleo.ser:
    response = nucleo.send_command("TEST")
    logger.info("Response: %s", response)
else:
    logger.error("Serial port not available.")
