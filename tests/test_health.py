import unittest

from health_assistant import daily_health_tip


class TestDailyHealthTip(unittest.TestCase):
    def test_returns_a_string(self):
        self.assertIsInstance(daily_health_tip(), str)

    def test_tip_is_non_empty(self):
        self.assertTrue(daily_health_tip().strip())


if __name__ == "__main__":
    unittest.main()
