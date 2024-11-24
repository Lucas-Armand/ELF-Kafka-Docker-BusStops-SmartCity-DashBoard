#!/bin/bash

# Kibana Export API: https://www.elastic.co/docs/api/doc/kibana/v8/operation/operation-exportsavedobjectsdefault
curl -X POST "http://localhost:5601/api/saved_objects/_export" \
-H "kbn-xsrf: true" \
-H "Content-Type: application/json; Elastic-Api-Version=2023-10-31" \
-d '{
  "type": ["index-pattern", "visualization", "dashboard"],
  "excludeExportDetails": true
}' -o kibana_export.ndjson
