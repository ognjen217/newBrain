import unittest
from apis.bosch_api import BoschAPI
from apis.simulated_server import SimulatedServer

class TestBoschAPI(unittest.TestCase):
    def setUp(self):
        self.config = {"endpoint": "https://example.com/api", "api_key": "testkey", "timeout": 2}
        self.api = BoschAPI(self.config)
    
    def test_send_data(self):
        data = {"sample": "data"}
        response = self.api.send_data(data)
        # Očekujemo da je response rečnik i sadrži ključ "status"
        self.assertIsInstance(response, dict)
        self.assertIn("status", response)

class TestSimulatedServer(unittest.TestCase):
    def setUp(self):
        # Postavljamo success_rate=1.0 da bismo osigurali uspešan odgovor
        self.config = {"delay": 0.1, "success_rate": 1.0}
        self.server = SimulatedServer(self.config)
    
    def test_process_request_success(self):
        data = {"key": "value"}
        response = self.server.process_request(data)
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["data"], data)

if __name__ == "__main__":
    unittest.main()
