#!/bin/sh
set -eu
umask 077
cd "$(dirname "$0")"

if [ -e .env ]; then
    echo 'Using existing deployment environment.'
    exit 0
fi

tmp=$(mktemp .env.XXXXXX)
trap 'rm -f "$tmp"' EXIT
{
    printf 'MYSQL_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 32)"
    printf 'MYSQL_PASSWORD=%s\n' "$(openssl rand -hex 32)"
    printf 'WALLE_JWT_SECRET=%s\n' "$(openssl rand -hex 32)"
    printf 'WALLE_DEVICE_API_TOKEN=%s\n' "$(openssl rand -hex 32)"
    printf 'ONENET_TOKEN=%s\n' "$(openssl rand -hex 32)"
    printf 'WALLE_ADMIN_PASSWORD=%s\n' "$(openssl rand -hex 16)"
} > "$tmp"
mv "$tmp" .env
trap - EXIT
echo 'Created deployment environment with restricted permissions.'
