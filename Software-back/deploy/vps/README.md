# WALL-E VPS deployment

This deployment runs the Java backend and a new MySQL database in the
`walle-server` Docker Compose project. The existing VPS services use separate
containers and volumes. MySQL is not published on the host; the backend and
Socket.IO ports are bound to loopback and exposed through the existing HTTPS
server.

- API: `https://zhanhui.cloud/walle/api`
- Health: `https://zhanhui.cloud/walle/actuator/health`
- Socket.IO server: `https://zhanhui.cloud`, path `/socket.io/`
- Management frontend: `https://zhanhui.cloud/walle/`
- Server directory: `/opt/walle-server`, with secrets in `.env` (mode 600)
- Administrator and device access details: `access.env` (mode 600)
- Database data: Docker volume `walle-server_mysql_data`
- Voice files: Docker volume `walle-server_voice_data`

The database was initialized without the repository's default administrator.
`bootstrap-admin.sh` creates the administrator once with a random password;
it does not reset an existing account. The public registration and telemetry
endpoints require the `X-Walle-Device-Token` header. The existing registration
page has no field for this token, so registration through that page needs a
client update. The device token is also required when a robot joins Socket.IO;
the updated `Hardware-pi` files in this checkout send it. Video clients send
their user JWT when joining. These client changes must be installed on the
actual hardware or frontend before they take effect.

The server-side environment values in `access.env` can be supplied to the
robot's service manager. Set the OneNET console callback to
`https://zhanhui.cloud/walle/onenet/callback` and use `ONENET_TOKEN` from the
private access file if OneNET forwarding is needed. The GPU AI and voice
services are not included in this deployment and their addresses must be
configured separately when available.

Operations on the VPS:

```sh
cd /opt/walle-server
docker compose ps
docker compose logs --tail=100 backend
sh backup-db.sh
WALLE_BASE_URL=https://zhanhui.cloud/walle WALLE_SOCKET_URL=https://zhanhui.cloud python3 smoke.py
```

The backup script writes a restricted, compressed SQL dump under
`/opt/walle-server/backups`. A systemd timer runs it daily; there is no
automatic off-server copy. Never rerun the upstream initialization script
against an existing database: it resets the default admin and config.
