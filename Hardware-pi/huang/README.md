# Raspberry Pi code snapshot

This directory is a snapshot of `/home/pi/walle/huang`. Python virtual
environments, caches, IDE settings, and historical backups are omitted.

Credentials have been removed from the uploaded copies of `config.py`,
`l610_manager.py`, `mqtt_manager.py`, `static/app1.py`, `templates/app1.py`,
`templates/app2.py`, and `templates/shipintonghua.py`. The original files on
the Pi are unchanged.
Set the following environment variables before starting the corresponding
services:

- `WALLE_SECRET_KEY`: Flask session signing key.
- `WALLE_LOGIN_PASSWORD`: web interface login password.
- `WALLE_DEVICE_API_TOKEN`: OneNet and device API token.
- `WALLE_MQTT_PASSWORD`: L610 MQTT password.
- `WALLE_EVENT_JWT_SECRET_BASE64`: base64-encoded event API JWT signing key.
- `WALLE_API_TOKEN`: optional API authentication token when API auth is enabled.

Missing variables default to empty values. Login and event requests are
disabled until their credentials are configured. Sessions and service
connections require the appropriate values.

`templates/app1.py` contains null bytes in the original Pi file and does not
pass Python syntax compilation. Its uploaded copy has had credentials removed;
the existing file corruption remains.
