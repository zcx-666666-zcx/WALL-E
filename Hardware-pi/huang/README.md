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
- `WALLE_DEVICE_API_TOKEN`: backend device API token, also used for signaling and camera frames.
- `WALLE_ONENET_TOKEN`: OneNET MQTT token, separate from the backend device token.
- `WALLE_MQTT_PASSWORD`: L610 MQTT password.
- `WALLE_API_TOKEN`: optional API authentication token when API auth is enabled.

Missing variables default to empty values. Login and event requests are
disabled until their credentials are configured. Sessions and service
connections require the appropriate values.

## Updating an existing robot

Back up the robot's existing files and service configuration before updating.
The repository copy of `config.py` has been sanitized: do not overwrite a
working local configuration without preserving its existing credentials and
device-specific settings. Apply the config changes deliberately and set
`WALLE_DEVICE_API_TOKEN` and `WALLE_ONENET_TOKEN` separately in the environment
of every service that needs them. Obtain the device token privately from the
deployment administrator; do not commit credentials to Git.

The backend device ID defaults to `WALLE_1`, while the existing OneNET device
name remains `WALEE_1`. The signaling server defaults to `https://zhanhui.cloud`.
After updating, restart the existing robot service with its configured
environment. Its logs should show a successful `robot_WALLE_1`/`robot_WALEE_1`
room join and periodic camera-frame sends. A `join_error` or `unauthorized`
message indicates that the backend device token or service environment needs
checking. A missing or stale camera frame will not be pushed.
Optional `WALLE_RTC_AUDIO_INPUT` and `WALLE_RTC_AUDIO_OUTPUT` select ALSA devices
(default: `default`); an empty value disables the corresponding direction.
Test camera, microphone, speaker, and motor behavior on the actual device.
The remote-control watchdog sends a stop after 0.8 seconds without fresh
movement commands or on disconnect. Keep the robot in a safe test area.
Health values remain demo values when live sensor readings are unavailable.

The hardware AI conversation bridge listens on `127.0.0.1:18765` and uses
the existing web switch to enable or disable microphone capture. It defaults
to disabled and sends speech through the authenticated HTTPS AI service.
This replaces the computer-side audio relay; the optional desktop YOLO vision
tracking program remains separate. To use the older external audio receiver,
set both `WALLE_AUDIO_SERVER_IP` and `WALLE_AUDIO_SERVER_PORT` in the service
environment. Video calls default to no audio; enable it before joining if
needed. Event reminders use `WALLE_EVENT_REFERENCE_AUDIO` and
`WALLE_EVENT_REFERENCE_TEXT` when configured, then fall back to the original
speech path on failure. Keep reference audio and credentials outside Git.

The 2026-11-28 device profile uses a 1280x720 shared camera frame for WebRTC,
while `WALLE_CAMERA_PUSH_WIDTH=640` and `WALLE_CAMERA_PUSH_FPS=8` limit the
separate remote-control JPEG feed. These settings are device/network specific;
verify CPU, uplink and camera support before applying them elsewhere. Event
polling defaults to five seconds and can be adjusted with
`WALLE_EVENT_POLL_INTERVAL` (minimum five seconds).

`templates/app1.py` contains null bytes in the original Pi file and does not
pass Python syntax compilation. Its uploaded copy has had credentials removed;
the existing file corruption remains.
