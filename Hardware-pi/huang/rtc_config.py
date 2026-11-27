import logging


def offer_has_audio(sdp):
    return any(line.startswith('m=audio ') and line.split()[1] != '0'
               for line in sdp.splitlines() if len(line.split()) >= 2)


def fetch_ice_servers(base_url, token, get):
    try:
        response = get(base_url.rstrip('/') + '/rtc/ice',
                       headers={'X-Walle-Device-Token': token}, timeout=8)
        if response.status_code != 200:
            raise ValueError(f'HTTP {response.status_code}')
        servers = response.json().get('iceServers')
        if not isinstance(servers, list) or not servers:
            raise ValueError('invalid ICE server list')
        return servers
    except Exception as exc:
        logging.getLogger('WebRTC_Client').warning('Video relay unavailable: %s', exc)
        return [{'urls': ['stun:stun.l.google.com:19302']}]
