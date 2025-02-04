import logging

class MotorControl:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("MotorControl")
        self.max_speed = config.get("max_speed", 10)
        self.min_speed = config.get("min_speed", 0)
        self.acceleration_step = config.get("acceleration_step", 1)
        self.deceleration_step = config.get("deceleration_step", 1)
        self.current_speed = 0
        self.logger.info("MotorControl inicijalizovan (max_speed=%s, min_speed=%s)", self.max_speed, self.min_speed)

    def accelerate(self):
        if self.current_speed + self.acceleration_step <= self.max_speed:
            self.current_speed += self.acceleration_step
        else:
            self.current_speed = self.max_speed
        self.logger.info("Ubrzavanje: trenutna brzina = %s", self.current_speed)

    def decelerate(self):
        if self.current_speed - self.deceleration_step >= self.min_speed:
            self.current_speed -= self.deceleration_step
        else:
            self.current_speed = self.min_speed
        self.logger.info("Kočenje: trenutna brzina = %s", self.current_speed)

    def maintain_speed(self):
        self.logger.info("Održavanje brzine: %s", self.current_speed)

    def stop(self):
        self.current_speed = 0
        self.logger.info("Motori su zaustavljeni.")

    def set_speed(self, speed):
        if speed > self.max_speed:
            self.current_speed = self.max_speed
        elif speed < self.min_speed:
            self.current_speed = self.min_speed
        else:
            self.current_speed = speed
        self.logger.info("Brzina postavljena na: %s", self.current_speed)
