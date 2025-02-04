import unittest
from utils.helpers import merge_dicts, validate_config
from utils.logger import get_logger
from utils.parallel import run_in_thread, run_in_process, run_in_process_pool
import time

class TestHelpers(unittest.TestCase):
    def test_merge_dicts(self):
        dict_a = {"a": 1, "b": 2}
        dict_b = {"b": 3, "c": 4}
        merged = merge_dicts(dict_a, dict_b)
        self.assertEqual(merged, {"a": 1, "b": 3, "c": 4})
    
    def test_validate_config(self):
        config = {"key1": "value1", "key2": "value2"}
        valid, missing = validate_config(config, ["key1", "key2"])
        self.assertTrue(valid)
        self.assertEqual(missing, [])
        valid, missing = validate_config(config, ["key1", "key3"])
        self.assertFalse(valid)
        self.assertIn("key3", missing)

class TestLogger(unittest.TestCase):
    def test_get_logger(self):
        logger = get_logger("TestLogger", level=10)
        self.assertEqual(logger.level, 10)

class TestParallel(unittest.TestCase):
    def test_run_in_thread(self):
        result = []
        def dummy_func(x):
            result.append(x * 2)
        thread = run_in_thread(dummy_func, args=(5,))
        thread.join(1)
        self.assertEqual(result[0], 10)
    
    def test_run_in_process(self):
        # Za testiranje procesa koristimo run_in_process_pool koji vraća rezultate
        def dummy_func(x):
            return x * 3
        args_list = [(3,), (4,)]
        results = run_in_process_pool(dummy_func, args_list)
        self.assertEqual(results, [9, 12])

if __name__ == "__main__":
    unittest.main()
