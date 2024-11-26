from kafka import KafkaConsumer, KafkaProducer
import json

KAFKA_BROKER = "kafka:9092"
RAW_TOPIC = "stop_raw"
PROCESSED_TOPIC = "stop"


def process_stop_raw_to_stop_format(data):
    transformed_data = {
        "location": {
            "lat": data["stop_lat"],
            "lon": data["stop_lon"]
        },
        "temperature": data["temperature"],
        "weather": data["weather"],
        "waiting_size": data["waiting_size"],
        "percentile_waiting_size": data["percentile_waiting_size"],
        "flood_detected": data["flood_detected"],
        "expected_wait_time_next_bus": data["expected_wait_time_next_bus"],
        "type": "stop_station",
        "stop_id": data["stop_id"]
    }
    return transformed_data


def main(producer, consumer):
    print(f"Listening to topic: {RAW_TOPIC}")
    for data in consumer:
        try:
            raw_data = data.value
            print(f"Received data: {raw_data}")

            transformed_data = process_stop_raw_to_stop_format(raw_data)
            print(f"Transformed: {transformed_data}")

            producer.send(PROCESSED_TOPIC, value=transformed_data)
            producer.flush()
            print(f"Published to topic: {PROCESSED_TOPIC}")
        except Exception as e:
            print(f"Error processing: {e}")


# Configurar o consumidor Kafka
consumer = KafkaConsumer(
    RAW_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='bus_processor_group'
)

# Configurar o produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print('start')
main(producer, consumer)
