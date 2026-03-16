#!/usr/bin/env bash
echo "Starting Kafka configuration"
pip install --no-cache-dir kafka-python
python3 /conf/kafka_config.py
echo "Ending Kafka configuration"

