#!/bin/sh
set -eu
umask 077
cd "$(dirname "$0")"
. ./.env

admin_count=$(docker compose exec -T mysql sh -c \
    'MYSQL_PWD="$MYSQL_PASSWORD" mysql -h 127.0.0.1 -u "$MYSQL_USER" -D "$MYSQL_DATABASE" -Nse "SELECT COUNT(*) FROM user WHERE username = '\''admin'\''"')
if [ "$admin_count" = 0 ]; then
    response=$(curl -fsS --max-time 15 -X POST http://127.0.0.1:18080/api/users/register \
        -H 'Content-Type: application/json' \
        -H "X-Walle-Device-Token: $WALLE_DEVICE_API_TOKEN" \
        --data "{\"username\":\"admin\",\"password\":\"$WALLE_ADMIN_PASSWORD\"}")
    printf '%s' "$response" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("code") == 1 else 1)'
    docker compose exec -T mysql sh -c \
        'MYSQL_PWD="$MYSQL_PASSWORD" mysql -h 127.0.0.1 -u "$MYSQL_USER" -D "$MYSQL_DATABASE" -e "UPDATE user SET role = '\''admin'\'' WHERE username = '\''admin'\''"'
    echo 'Created administrator.'
else
    echo 'Administrator already exists; no credentials changed.'
fi
