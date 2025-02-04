import logging

class MotorControl:
    def __init__(self, config):
        """
        Inicijalizacija sistema za kontrolu motora.
        :param config: Rečnik sa parametrima, npr.:
            {
                "max_speed": 10,
                "min_speed": 0,
                "acceleration_step": 1,
                "deceleration_step": 1
            }
        """
        self.config = config
        self.logger = logging.getLogger("MotorControl")
        self.max_speed = config.get("max_speed", 10)
        self.min_speed = config.get("min_speed", 0)
        self.acceleration_step = config.get("acceleration_step", 1)
        self.deceleration_step = config.get("deceleration_step", 1)
        self.current_speed = 0
        self.logger.info("MotorControl inicijalizovan (max_speed=%s, min_speed=%s)", self.max_speed, self.min_speed)

    def accelerate(self):
        """
        Povećava trenutnu brzinu, simulirajući ubrzanje.
        """
        if self.current_speed + self.acceleration_step <= self.max_speed:
            self.current_speed += self.acceleration_step
        else:
            self.current_speed = self.max_speed
        self.logger.info("Ubrzavanje: trenutna brzina = %s", self.current_speed)
        # TODO: Implementirati slanje odgovarajućih signala ka hardveru

    def decelerate(self):
        """
        Smanjuje trenutnu brzinu, simulirajući kočenje.
        """
        if self.current_speed - self.deceleration_step >= self.min_speed:
            self.current_speed -= self.deceleration_step
        else:
            self.current_speed = self.min_speed
        self.logger.info("Kočenje: trenutna brzina = %s", self.current_speed)
        # TODO: Implementirati slanje kočionog signala ka hardveru

    def maintain_speed(self):
        """
        Održava trenutnu brzinu.
        """
        self.logger.info("Održavanje brzine: %s", self.current_speed)
        # TODO: Ako je potrebno, implementirati logiku za održavanje brzine

    def stop(self):
        """
        Hitno zaustavlja motore.
        """
        self.current_speed = 0
        self.logger.info("Motori su zaustavljeni.")
        # TODO: Implementirati hitno zaustavljanje na hardverskom nivou

    def set_speed(self, speed):
        """
        Postavlja željenu brzinu, vodeći računa o granicama.
        :param speed: Željena brzina.
        """
        if speed > self.max_speed:
            self.current_speed = self.max_speed
        elif speed < self.min_speed:
            self.current_speed = self.min_speed
        else:
            self.current_speed = speed
        self.logger.info("Brzina postavljena na: %s", self.current_speed)
        # TODO: Slati odgovarajuću komandu hardveru
