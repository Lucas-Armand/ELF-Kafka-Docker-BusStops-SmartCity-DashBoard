#!/bin/bash

apt-get update && apt-get install -y curl

until curl -s -X GET "http://kibana:5601/api/status" -H 'kbn-xsrf: true' | grep -q '"state":"green"'; do
  echo 'Kibana is not ready...'
  sleep 5
done


# Elasticsearch Index Mapping: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html#mappings
curl -X PUT "http://elasticsearch:9200/bus?pretty" \
-H "Content-Type: application/json" \
-d '{
  "mappings": {
    "properties": {
      "bus_id": {"type": "keyword"},
      "location": {"type": "geo_point"},
      "timestamp": {"type": "date"}
    }
  }
}'

curl -X PUT "http://elasticsearch:9200/van?pretty" \
-H "Content-Type: application/json" \
-d '{
  "mappings": {
    "properties": {
      "van_id": {"type": "keyword"},
      "location": {"type": "geo_point"},
      "timestamp": {"type": "date"}
    }
  }
}'

curl -X PUT "http://elasticsearch:9200/stop_station?pretty" \
-H "Content-Type: application/json" \
-d '{
  "mappings": {
    "properties": {
      "location": {
        "type": "geo_point"
      },
      "temperature": {
        "type": "float"
      },
      "weather": {
        "type": "keyword"
      },
      "waiting_size": {
        "type": "float"
      },
      "percentile_waiting_size": {
        "type": "float"
      },
      "flood_detected": {
        "type": "boolean"
      },
      "expected_wait_time_next_bus": {
        "type": "float"
      },
      "timestamp": {
        "type": "date"
      }
    }
  }
}'



# Kibana Import API: https://www.elastic.co/guide/en/kibana/current/saved-objects-api-import.html
curl -X POST "http://kibana:5601/api/saved_objects/_import" \
-H "kbn-xsrf: true" \
-F file=@/conf/kibana_export.ndjson

# Config Kafka:
echo 'Stating Kafka Configuration'
pip install kafka-python
python3 /conf/kafka_config.py
echo 'Ending Kafka Configuration'
