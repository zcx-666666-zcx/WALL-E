import importlib.util
import pathlib
import unittest
from unittest.mock import Mock

path = pathlib.Path(__file__).resolve().parents[1] / 'motor_watchdog.py'
spec = importlib.util.spec_from_file_location('motor_watchdog', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MotorWatchdogTest(unittest.TestCase):
    def test_stale_commands_stop_and_new_commands_remain_active(self):
        now = [100.0]
        output = Mock()
        guard = module.MotorWatchdog(output, clock=lambda: now[0], timeout=0.8)
        guard.move(0.5, -0.3)
        output.assert_any_call('X50')
        output.assert_any_call('Y-30')
        now[0] += 0.5
        guard.check()
        self.assertEqual(output.call_count, 2)
        guard.move(0.2, 0.1)
        now[0] += 0.5
        guard.check()
        self.assertEqual(output.call_count, 4)
        now[0] += 0.4
        guard.check()
        self.assertEqual([c.args[0] for c in output.call_args_list[-2:]], ['X0', 'Y0'])
        guard.check()
        self.assertEqual(output.call_count, 6)

    def test_rejects_nonfinite_and_out_of_range_motion(self):
        output = Mock()
        guard = module.MotorWatchdog(output)
        for x, y in [(float('nan'), 0), (2, 0), (0, float('inf'))]:
            with self.assertRaises(ValueError):
                guard.move(x, y)
        output.assert_not_called()

    def test_disconnect_stop_sends_zero_even_without_prior_motion(self):
        output = Mock()
        module.MotorWatchdog(output).stop()
        self.assertEqual([c.args[0] for c in output.call_args_list], ['X0', 'Y0'])
