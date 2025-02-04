import logging
import time
import threading

class SensorManager:
    def __init__(self, config):
        """
        Inicijalizacija sensor manager-a.
        :param config: Rečnik sa konfiguracionim parametrima, npr.:
            {
                "acquisition_interval": 0.1  # interval u sekundama
            }
        """
        self.config = config
        self.logger = logging.getLogger("SensorManager")
        self.acquisition_running = False
        self.data_lock = threading.Lock()
        self.latest_data = {}
        self.logger.info("SensorManager inicijalizovan sa konfiguracijom: %s", config)

    def start_acquisition(self):
        """
        Pokreće akviziciju senzorskih podataka.
        Ova metoda se preporučuje da se pokrene u zasebnoj niti.
        """
        self.acquisition_running = True
        self.logger.info("Početak akvizicije senzorskih podataka.")
        while self.acquisition_running:
            sensor_data = self._read_sensors()
            with self.data_lock:
                self.latest_data = sensor_data
            time.sleep(self.config.get("acquisition_interval", 0.1))

    def _read_sensors(self):
        """
        Simulira čitanje podataka sa senzora.
        Vraća rečnik sa primerom podataka.
        """
        # Ova metoda treba biti zamenjena stvarnim kodom za čitanje senzora
        imu_data = {"acceleration": [0, 0, 0], "gyro": [0, 0, 0]}
        camera_data = {"image": None}  # Mesto za integraciju sa sistemom kamere
        speed_data = {"speed": 0}
        sensor_data = {**imu_data, **camera_data, **speed_data}
        self.logger.debug("Pročitani senzorski podaci: %s", sensor_data)
        return sensor_data

    def get_latest_data(self):
        """
        Vraća najnovije prikupljene senzorske podatke.
        """
        with self.data_lock:
            return self.latest_data.copy()

    def stop_acquisition(self):
        """
        Prekida akviziciju podataka.
        """
        self.acquisition_running = False
        self.logger.info("Zaustavljanje akvizicije senzorskih podataka.")
