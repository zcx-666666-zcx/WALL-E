#!/bin/sh
set -eu
umask 077
cd "$(dirname "$0")"
mkdir -p backups
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
tmp=$(mktemp "backups/.walle-$timestamp.XXXXXX")
target="backups/walle-$timestamp-$(openssl rand -hex 4).sql.gz"
trap 'rm -f "$tmp" "$tmp.gz"' EXIT
docker compose exec -T mysql sh -c \
    'MYSQL_PWD="$MYSQL_PASSWORD" mysqldump -h 127.0.0.1 -u "$MYSQL_USER" --single-transaction --no-tablespaces "$MYSQL_DATABASE"' \
    > "$tmp"
gzip -c "$tmp" > "$tmp.gz"
gzip -t "$tmp.gz"
mv "$tmp.gz" "$target"
rm -f "$tmp"
trap - EXIT
echo "Backup created: $target"
