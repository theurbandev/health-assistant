import contextlib
import io
import unittest

from health_assistant.cli import main


class TestCli(unittest.TestCase):
    def test_tips_prints_daily_health_tip(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            exit_code = main(["tips"])

        self.assertEqual(exit_code, 0)
        self.assertTrue(output.getvalue().strip())

    def test_missing_command_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main([])


if __name__ == "__main__":
    unittest.main()
