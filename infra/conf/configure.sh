#!/usr/bin/env bash
set -euo pipefail

apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
rm -rf /var/lib/apt/lists/*

: "${ELASTIC_PASSWORD:?ELASTIC_PASSWORD não definido}"

KIBANA_URL="http://kibana:5601"
ES_URL="https://elasticsearch:9200"
CA_CERT="/certs/ca/ca.crt"
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

BUS_MAPPING='{
  "mappings": {
    "properties": {
      "bus_id": {"type": "keyword"},
      "location": {"type": "geo_point"},
      "timestamp": {"type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis"}
    }
  }
}'

VAN_MAPPING='{
  "mappings": {
    "properties": {
      "van_id": {"type": "keyword"},
      "location": {"type": "geo_point"},
      "timestamp": {"type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis"}
    }
  }
}'

STOP_MAPPING='{
  "mappings": {
    "properties": {
      "location": {"type": "geo_point"},
      "temperature": {"type": "float"},
      "weather": {"type": "keyword"},
      "waiting_size": {"type": "float"},
      "percentile_waiting_size": {"type": "float"},
      "flood_detected": {"type": "boolean"},
      "expected_wait_time_next_bus": {"type": "float"},
      "timestamp": {"type": "date", "format": "strict_date_optional_time||epoch_second||epoch_millis"}
    }
  }
}'

create_index_if_missing "bus" "$BUS_MAPPING"
create_index_if_missing "van" "$VAN_MAPPING"
create_index_if_missing "stop_station" "$STOP_MAPPING"

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

