import base64
import hashlib
import hmac
import secrets
import time


def issue_ice_servers(secret, host, now=None):
    if not secret or not host:
        raise ValueError('TURN relay is not configured')
    expires = int(time.time() if now is None else now) + 3600
    username = f'{expires}:{secrets.token_hex(8)}'
    credential = base64.b64encode(hmac.new(secret.encode(), username.encode(), hashlib.sha1).digest()).decode()
    return [
        {'urls': [f'stun:{host}:3478']},
        {'urls': [f'turn:{host}:3478?transport=tcp', f'turn:{host}:3478?transport=udp'],
         'username': username, 'credential': credential},
    ]
