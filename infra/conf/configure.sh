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


echo "Ensuring kibana_system password is set..."
curl -s -X POST --cacert "$CA_CERT" \
  -u "elastic:${ELASTIC_PASSWORD}" \
  -H "Content-Type: application/json" \
  https://elasticsearch:9200/_security/user/kibana_system/_password \
  -d "{\"password\":\"${KIBANA_PASSWORD}\"}" | cat

echo "Done setting kibana_system password."


put_index_template () {
  local template_name="$1"
  local body="$2"

  echo "Applying index template: ${template_name}"
  curl -sS --cacert "$CA_CERT" -u "$AUTH" \
    -X PUT "${ES_URL}/_index_template/${template_name}" \
    -H "Content-Type: application/json" \
    -d "$body"
  echo
}

create_index_if_missing () {
  local index="$1"
  local body="$2"

  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    --cacert "$CA_CERT" -u "$AUTH" -X HEAD "${ES_URL}/${index}")

  if [ "$code" = "404" ]; then
    echo "Creating index: ${index}"
    curl -sS --cacert "$CA_CERT" -u "$AUTH" \
      -X PUT "${ES_URL}/${index}" \
      -H "Content-Type: application/json" \
      -d "$body"
    echo
  else
    echo "Index already exists: ${index} (HTTP ${code})"
  fi
}

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

BUS_TEMPLATE='{
  "index_patterns": ["bus"],
  "template": {
    "mappings": {
      "properties": {
        "bus_id": { "type": "keyword" },
        "type": { "type": "keyword" },
        "timestamp": { "type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis" },
        "@timestamp": { "type": "date" },
        "occupancy_status": { "type": "keyword" },
        "route_id": { "type": "keyword" },
        "trip_id": { "type": "keyword" },
        "stop_id": { "type": "keyword" },
        "current_status": { "type": "keyword" },
        "current_stop_sequence": { "type": "integer" },
        "entity_id": { "type": "keyword" },
        "entity_type": { "type": "keyword" },
        "schema_version": { "type": "keyword" },
        "location": { "type": "geo_point" }
      }
    }
  }
}'


STOP_TEMPLATE='{
  "index_patterns": ["stop_station"],
  "template": {
    "mappings": {
      "properties": {
        "location": { "type": "geo_point" },
        "temperature": { "type": "float" },
        "weather": { "type": "keyword" },
        "waiting_size": { "type": "float" },
        "percentile_waiting_size": { "type": "float" },
        "flood_detected": { "type": "boolean" },
        "expected_wait_time_next_bus": { "type": "float" },
        "timestamp": { "type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis" },
        "@timestamp": { "type": "date" }
      }
    }
  }
}'

BUS_INDEX_BOOTSTRAP='{
  "mappings": {
    "properties": {
      "bus_id": { "type": "keyword" },
      "type": { "type": "keyword" },
      "timestamp": { "type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis" },
      "@timestamp": { "type": "date" },
      "occupancy_status": { "type": "keyword" },
      "location": { "type": "geo_point" }
    }
  }
}'


STOP_INDEX_BOOTSTRAP='{
  "mappings": {
    "properties": {
      "location": { "type": "geo_point" },
      "temperature": { "type": "float" },
      "weather": { "type": "keyword" },
      "timestamp": { "type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis" },
      "@timestamp": { "type": "date" }
    }
  }
}'

put_index_template "bus-template" "$BUS_TEMPLATE"
put_index_template "stop-station-template" "$STOP_TEMPLATE"

create_index_if_missing "bus" "$BUS_INDEX_BOOTSTRAP"
create_index_if_missing "stop_station" "$STOP_INDEX_BOOTSTRAP"

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

echo "Starting Kafka configuration"
pip install --no-cache-dir kafka-python
python3 /conf/kafka_config.py
echo "Ending Kafka configuration"

