import base64
import hashlib
import hmac
import unittest

from turn_credentials import issue_ice_servers


class TurnCredentialsTest(unittest.TestCase):
    def test_issues_temporary_turn_rest_credentials(self):
        servers = issue_ice_servers('relay-secret', 'example.org', now=1000)
        self.assertEqual(servers[0]['urls'], ['stun:example.org:3478'])
        turn = servers[1]
        self.assertEqual(turn['username'].split(':')[0], '4600')
        expected = base64.b64encode(hmac.new(b'relay-secret', turn['username'].encode(), hashlib.sha1).digest()).decode()
        self.assertEqual(turn['credential'], expected)
        self.assertIn('turn:example.org:3478?transport=udp', turn['urls'])
        self.assertIn('turn:example.org:3478?transport=tcp', turn['urls'])

    def test_requires_configured_relay(self):
        with self.assertRaises(ValueError):
            issue_ice_servers('', 'example.org')
