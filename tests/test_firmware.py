import unittest
from firmware.motor_control import MotorControl
from firmware.sensor_manager import SensorManager
from firmware.nucleo_comm import NucleoComm

class TestMotorControl(unittest.TestCase):
    def setUp(self):
        self.config = {
            "max_speed": 10,
            "min_speed": 0,
            "acceleration_step": 2,
            "deceleration_step": 2,
            "default_speed": 5
        }
        self.motor = MotorControl(self.config)
    
    def test_accelerate(self):
        self.motor.current_speed = 0
        self.motor.accelerate()
        self.assertEqual(self.motor.current_speed, 2)
    
    def test_decelerate(self):
        self.motor.current_speed = 8
        self.motor.decelerate()
        self.assertEqual(self.motor.current_speed, 6)
    
    def test_stop(self):
        self.motor.current_speed = 8
        self.motor.stop()
        self.assertEqual(self.motor.current_speed, 0)

class TestSensorManager(unittest.TestCase):
    def setUp(self):
        self.config = {"acquisition_interval": 0.01}
        self.sensor_manager = SensorManager(self.config)
        # Za testiranje ne pokrećemo stvarnu petlju akvizicije
        self.sensor_manager.acquisition_running = False
    
    def test_get_latest_data(self):
        # Direktno pozivanje privatne metode _read_sensors (za potrebe testa)
        data = self.sensor_manager._read_sensors()
        self.assertIn("acceleration", data)
        self.assertIn("gyro", data)
        self.assertIn("speed", data)

class TestNucleoComm(unittest.TestCase):
    def setUp(self):
        self.config = {"port": "COM1", "baudrate": 9600}
        self.nucleo = NucleoComm(self.config)
    
    def test_send_command(self):
        command = "TEST_COMMAND"
        response = self.nucleo.send_command(command)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["command"], command)

if __name__ == "__main__":
    unittest.main()
