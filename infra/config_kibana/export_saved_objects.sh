#!/usr/bin/env bash
set -euo pipefail

: "${ELASTIC_PASSWORD:?ELASTIC_PASSWORD não definido}"

# Se você rodar isso FORA do docker, use:
# export KIBANA_URL="http://localhost:54321"
KIBANA_URL="${KIBANA_URL:-http://kibana:5601}"

curl -sS -u "elastic:${ELASTIC_PASSWORD}" \
  -X POST "${KIBANA_URL}/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "type": ["index-pattern", "visualization", "dashboard"],
    "excludeExportDetails": true
  }' -o kibana_export.ndjson

