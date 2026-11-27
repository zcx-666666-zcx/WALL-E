import importlib.util
import pathlib
import unittest
from unittest.mock import Mock

path = pathlib.Path(__file__).resolve().parents[1] / 'rtc_config.py'
spec = importlib.util.spec_from_file_location('rtc_config', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RtcConfigTest(unittest.TestCase):
    def test_gets_temporary_relay_credentials_using_device_token(self):
        get = Mock(return_value=Mock(status_code=200, json=lambda: {'iceServers': [
            {'urls': ['turn:example.org:3478?transport=udp'], 'username': 'temporary', 'credential': 'secret'}]}))
        servers = module.fetch_ice_servers('https://example.org/walle/ai', 'device-token', get)
        self.assertEqual(servers[0]['username'], 'temporary')
        self.assertEqual(get.call_args.kwargs['headers'], {'X-Walle-Device-Token': 'device-token'})

    def test_failure_falls_back_to_stun_without_leaking_credentials(self):
        get = Mock(side_effect=RuntimeError('offline'))
        servers = module.fetch_ice_servers('https://example.org/walle/ai', 'device-token', get)
        self.assertTrue(servers[0]['urls'][0].startswith('stun:'))
