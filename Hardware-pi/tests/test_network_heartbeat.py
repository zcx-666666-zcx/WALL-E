import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "network_heartbeat_under_test", ROOT / "network_heartbeat.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NetworkHeartbeatTest(unittest.TestCase):
    def test_heartbeat_sends_device_token_and_network_details(self):
        module = load_module()
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"code":1}'
        urlopen = mock.Mock(return_value=response)

        result = module.send_heartbeat(
            api_base_url="https://example.test/api",
            device_id="WALEE_1",
            device_token="device-secret",
            lan_ip="192.168.1.25",
            network_name="office-wifi",
            urlopen_impl=urlopen,
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://example.test/api/device/network/heartbeat/WALEE_1",
        )
        self.assertEqual(request.get_header("X-walle-device-token"), "device-secret")
        self.assertEqual(
            json.loads(request.data),
            {"lanIp": "192.168.1.25", "networkName": "office-wifi"},
        )
        self.assertEqual(result["code"], 1)

    def test_lan_ip_uses_active_route_address(self):
        module = load_module()
        sock = mock.MagicMock()
        sock.getsockname.return_value = ("10.0.0.8", 12345)
        socket_factory = mock.Mock(return_value=sock)

        address = module.discover_lan_ip(socket_factory=socket_factory)

        sock.connect.assert_called_once()
        sock.close.assert_called_once()
        self.assertEqual(address, "10.0.0.8")

    def test_missing_network_does_not_send_heartbeat(self):
        module = load_module()
        urlopen = mock.Mock()

        sent = module.report_current_network(
            api_base_url="https://example.test/api",
            device_id="WALLE_1",
            device_token="device-secret",
            ip_resolver=lambda: None,
            network_resolver=lambda: None,
            urlopen_impl=urlopen,
        )

        self.assertFalse(sent)
        urlopen.assert_not_called()

    def test_remote_plain_http_requires_explicit_opt_in(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.send_heartbeat(
                api_base_url="http://example.test/api",
                device_id="WALLE_1",
                device_token="device-secret",
                lan_ip="192.168.1.25",
                urlopen_impl=mock.Mock(),
            )

    def test_trusted_plain_http_can_be_enabled_explicitly(self):
        module = load_module()
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"code":1}'

        result = module.send_heartbeat(
            api_base_url="http://example.test/api",
            device_id="WALLE_1",
            device_token="device-secret",
            lan_ip="192.168.1.25",
            urlopen_impl=mock.Mock(return_value=response),
            allow_insecure=True,
        )

        self.assertEqual(result["code"], 1)

    def test_runtime_config_requires_url_and_token(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.read_runtime_config({})


if __name__ == "__main__":
    unittest.main()
