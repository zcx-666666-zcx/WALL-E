#!/bin/sh
set -eu
umask 077
cd /opt/walle-turn
test ! -e turnserver.conf
test ! -e turn-secret
openssl rand -hex 32 > turn-secret
secret=$(cat turn-secret)
{
  printf '%s\n' 'listening-port=3478' 'listening-ip=193.134.210.58' 'relay-ip=193.134.210.58'
  printf '%s\n' 'min-port=49160' 'max-port=49199' 'realm=zhanhui.cloud'
  printf '%s\n' 'use-auth-secret' "static-auth-secret=$secret" 'fingerprint'
  printf '%s\n' 'no-cli' 'no-tls' 'no-dtls' 'no-loopback-peers' 'no-multicast-peers'
  printf '%s\n' 'denied-peer-ip=0.0.0.0-0.255.255.255' 'denied-peer-ip=10.0.0.0-10.255.255.255'
  printf '%s\n' 'denied-peer-ip=127.0.0.0-127.255.255.255' 'denied-peer-ip=169.254.0.0-169.254.255.255'
  printf '%s\n' 'denied-peer-ip=172.16.0.0-172.31.255.255' 'denied-peer-ip=192.168.0.0-192.168.255.255'
  printf '%s\n' 'user-quota=4' 'total-quota=20' 'stale-nonce=600'
} > turnserver.conf
chown 65534:65534 turnserver.conf
chmod 600 turnserver.conf turn-secret
echo 'TURN configuration created.'
