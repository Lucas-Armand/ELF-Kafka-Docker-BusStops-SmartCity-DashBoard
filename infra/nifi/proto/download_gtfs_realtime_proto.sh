#!/usr/bin/env bash
set -euo pipefail

mkdir -p infra/nifi/proto

curl -L \
  https://raw.githubusercontent.com/google/transit/master/gtfs-realtime/proto/gtfs-realtime.proto \
  -o infra/nifi/proto/gtfs-realtime.proto

echo "OK: infra/nifi/proto/gtfs-realtime.proto"
