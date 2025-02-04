"""
Modul za komunikaciju sa Bosch serverima putem API-ja.

Očekivana konfiguracija (config dictionary) može izgledati ovako:
{
    "endpoint": "https://bosch.example.com/api",
    "api_key": "YOUR_API_KEY",
    "timeout": 5
}

Klasa BoschAPI koristi biblioteku `requests` da pošalje podatke u JSON formatu.
"""

import requests
import logging

class BoschAPI:
    def __init__(self, config):
        """
        Inicijalizacija BoschAPI sa datom konfiguracijom.
        """
        self.config = config
        self.endpoint = config.get("endpoint", "https://bosch.example.com/api")
        self.api_key = config.get("api_key", None)
        self.timeout = config.get("timeout", 5)
        self.logger = logging.getLogger("BoschAPI")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        self.logger.info("BoschAPI inicijalizovan sa endpointom: %s", self.endpoint)

    def send_data(self, data):
        """
        Metoda za slanje podataka na Bosch server.
        :param data: Rečnik sa podacima (npr. senzorski podaci)
        :return: Odgovor servera u JSON formatu ili rečnik sa informacijom o grešci.
        """
        try:
            self.logger.debug("Slanje podataka: %s", data)
            response = requests.post(
                self.endpoint,
                json=data,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            self.logger.info("Podaci uspešno poslati na Bosch API.")
            return response.json()
        except Exception as e:
            self.logger.error("Neuspešno slanje podataka na Bosch API: %s", e)
            # U slučaju greške, može se vratiti simulirani odgovor ili informacija o grešci.
            return {"status": "error", "message": str(e)}
