#!/bin/sh
set -eu
umask 077
cd "$(dirname "$0")"
. ./.env
tmp=$(mktemp .access.XXXXXX)
trap 'rm -f "$tmp"' EXIT
{
    printf 'WALLE_ADMIN_USERNAME=admin\n'
    printf 'WALLE_ADMIN_PASSWORD=%s\n' "$WALLE_ADMIN_PASSWORD"
    printf 'WALLE_DEVICE_API_TOKEN=%s\n' "$WALLE_DEVICE_API_TOKEN"
    printf 'ONENET_TOKEN=%s\n' "$ONENET_TOKEN"
    printf 'WALLE_PUBLIC_SERVER_URL=https://zhanhui.cloud/walle\n'
    printf 'WALLE_SERVER_URL=https://zhanhui.cloud\n'
    printf 'WALLE_SOCKETIO_SERVER_URL=https://zhanhui.cloud\n'
} > "$tmp"
mv "$tmp" access.env
trap - EXIT
echo 'Access details written with restricted permissions.'
