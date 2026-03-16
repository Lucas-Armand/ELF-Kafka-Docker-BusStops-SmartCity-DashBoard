#!/usr/bin/env bash
set -euo pipefail
set -x

apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
rm -rf /var/lib/apt/lists/*

: "${ELASTIC_PASSWORD:?ELASTIC_PASSWORD não definido}"

AUTH="elastic:${ELASTIC_PASSWORD}"

echo "Waiting for Elasticsearch..."
until curl -sS --fail --cacert "$CA_CERT" -u "$AUTH" \
  "${ES_URL}/_cluster/health?wait_for_status=yellow&timeout=5s" >/dev/null; do
  echo "Elasticsearch is not ready..."
  sleep 5
done
echo "Elasticsearch is ready."

echo "Ensuring kibana_system password is set..."
curl -s -X POST --cacert "$CA_CERT" \
  -u "$AUTH" \
  -H "Content-Type: application/json" \
  ${ES_URL}/_security/user/kibana_system/_password \
  -d "{\"password\":\"${KIBANA_PASSWORD}\"}" | cat

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
  code=$(curl -sS --max-time 10 -o /dev/null -w "%{http_code}" \
    --cacert "$CA_CERT" -u "$AUTH" \
    "${ES_URL}/${index}")

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

echo "Creating templates..."
put_index_template "bus-template" "$BUS_TEMPLATE"
put_index_template "stop-station-template" "$STOP_TEMPLATE"

echo "Creating bootstrap indices if needed..."
create_index_if_missing "bus" "$BUS_INDEX_BOOTSTRAP"
create_index_if_missing "stop_station" "$STOP_INDEX_BOOTSTRAP"

echo "Elastic bootstrap finished successfully."
