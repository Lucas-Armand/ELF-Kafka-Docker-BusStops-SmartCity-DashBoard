#!/usr/bin/env bash
set -euo pipefail

apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
rm -rf /var/lib/apt/lists/*

: "${ELASTIC_PASSWORD:?ELASTIC_PASSWORD não definido}"

AUTH="elastic:${ELASTIC_PASSWORD}"

echo "Waiting for Kibana..."
until curl -sS -u "$AUTH" "${KIBANA_URL}/api/status?v7format=true" | grep -q '"state":"green"'; do
  echo "Kibana is not ready..."
  sleep 5
done
echo "Kibana is ready."


create_data_view_if_missing () {
  local title="$1"
  local name="$2"
  local time_field="$3"

  echo "Ensuring Kibana data view exists for: ${title}"

  local existing
  existing=$(curl -sS -u "$AUTH" \
    -H "kbn-xsrf: true" \
    "${KIBANA_URL}/api/data_views/data_view" || true)

  if echo "$existing" | grep -q "\"title\":\"${title}\""; then
    echo "Data view already exists: ${title}"
    return 0
  fi

  curl -sS -u "$AUTH" \
    -X POST "${KIBANA_URL}/api/data_views/data_view" \
    -H "kbn-xsrf: true" \
    -H "Content-Type: application/json" \
    -d "{
      \"data_view\": {
        \"title\": \"${title}\",
        \"name\": \"${name}\",
        \"timeFieldName\": \"${time_field}\"
      }
    }"
  echo
}

create_data_view_if_missing "bus" "bus" "@timestamp"
create_data_view_if_missing "stop_station" "stop_station" "@timestamp"

# Import Kibana saved objects (pode falhar se o arquivo for de major antigo, ex: 7 -> 9)
if [ -f /conf/kibana_export_old.ndjson ]; then
  echo "Importing Kibana saved objects..."
  curl -sS -u "$AUTH" \
    -X POST "${KIBANA_URL}/api/saved_objects/_import?overwrite=true&compatibilityMode=true" \
    -H "kbn-xsrf: true" \
    -F file=@/conf/kibana_export_old.ndjson
  echo
else
  echo "No /conf/kibana_export_old.ndjson found. Skipping import."
fi
