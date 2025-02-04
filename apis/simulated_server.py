"""
Modul koji simulira server za testiranje API komunikacije.
Ovaj modul omogućava testiranje bez stvarnog poziva ka Bosch serverima.

Očekivana konfiguracija (config dictionary) može izgledati ovako:
{
    "delay": 0.5,          # Vreme (u sekundama) za simulaciju obrade zahteva
    "success_rate": 0.9      # Verovatnoća uspešnog odgovora (vrednost između 0 i 1)
}

Klasa SimulatedServer pruža metodu `process_request` koja simulira
obradu podataka i vraća odgovarajući rečnik.
"""

import time
import random
import logging

class SimulatedServer:
    def __init__(self, config):
        """
        Inicijalizacija SimulatedServer-a sa datom konfiguracijom.
        """
        self.config = config
        self.delay = config.get("delay", 0.5)
        self.success_rate = config.get("success_rate", 0.9)
        self.logger = logging.getLogger("SimulatedServer")
        self.logger.info("SimulatedServer inicijalizovan sa delay=%s i success_rate=%.2f",
                         self.delay, self.success_rate)

    def process_request(self, data):
        """
        Simulira obradu zahteva sa zadatim podacima.
        :param data: Rečnik sa podacima (npr. senzorski podaci)
        :return: Simulirani odgovor – rečnik koji označava uspeh ili grešku.
        """
        self.logger.info("SimulatedServer prima podatke: %s", data)
        # Simulacija kašnjenja u obradi
        time.sleep(self.delay)
        # Nasumično određivanje uspeha ili greške
        if random.random() < self.success_rate:
            response = {"status": "success", "data": data}
            self.logger.info("SimulatedServer: Obrada uspešna.")
        else:
            response = {"status": "error", "message": "Simulirana greška u obradi podataka"}
            self.logger.error("SimulatedServer: Došlo je do greške prilikom obrade.")
        return response

    def start(self):
        """
        (Opcionalno) Metoda za pokretanje simuliranog servera.
        Ukoliko se odlučite da server pokrećete kao HTTP server, ovde možete
        integrisati odgovarajući framework (npr. Flask). Trenutno je samo
        placeholder za buduće proširenje.
        """
        self.logger.info("SimulatedServer pokrenut (placeholder metod).")
