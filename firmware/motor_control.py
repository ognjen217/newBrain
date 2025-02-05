import logging

class MotorControl:
    def __init__(self, config, nucleo_comm=None):
        """
        Initialize motor control.
        :param config: Dictionary with motor parameters.
        :param nucleo_comm: Instance of NucleoComm.
        """
        self.config = config
        self.logger = logging.getLogger("MotorControl")
        self.max_speed = config.get("max_speed", 10)
        self.min_speed = config.get("min_speed", 0)
        self.acceleration_step = config.get("acceleration_step", 1)
        self.deceleration_step = config.get("deceleration_step", 1)
        self.current_speed = 0
        self.nucleo_comm = nucleo_comm
        self.logger.info("MotorControl initialized (max_speed=%s, min_speed=%s)", self.max_speed, self.min_speed)

    def accelerate(self):
        if self.current_speed + self.acceleration_step <= self.max_speed:
            self.current_speed += self.acceleration_step
        else:
            self.current_speed = self.max_speed
        self.logger.info("Accelerating: current speed = %s", self.current_speed)
        if self.nucleo_comm:
            self.nucleo_comm.send_command(f"SPEED:{self.current_speed}")

    def decelerate(self):
        if self.current_speed - self.deceleration_step >= self.min_speed:
            self.current_speed -= self.deceleration_step
        else:
            self.current_speed = self.min_speed
        self.logger.info("Decelerating: current speed = %s", self.current_speed)
        if self.nucleo_comm:
            self.nucleo_comm.send_command(f"SPEED:{self.current_speed}")

    def maintain_speed(self):
        self.logger.info("Maintaining speed: %s", self.current_speed)
        if self.nucleo_comm:
            self.nucleo_comm.send_command(f"MAINTAIN:{self.current_speed}")

    def stop(self):
        self.current_speed = 0
        self.logger.info("Motors stopped.")
        if self.nucleo_comm:
            self.nucleo_comm.send_command("STOP")

    def set_speed(self, speed):
        if speed > self.max_speed:
            self.current_speed = self.max_speed
        elif speed < self.min_speed:
            self.current_speed = self.min_speed
        else:
            self.current_speed = speed
        self.logger.info("Speed set to: %s", self.current_speed)
        if self.nucleo_comm:
            self.nucleo_comm.send_command(f"SPEED:{self.current_speed}")

