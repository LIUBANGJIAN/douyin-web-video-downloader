#!/bin/bash
set -e

mkdir -p /data/douyin /app/downloads

if [ ! -f /data/douyin/config.yaml ]; then
  printf 'Cookie: ""\n' > /data/douyin/config.yaml
fi

mkdir -p /douyin-api/crawlers/douyin/web
ln -sf /data/douyin/config.yaml /douyin-api/crawlers/douyin/web/config.yaml

exec supervisord -n -c /etc/supervisor/supervisord.conf
