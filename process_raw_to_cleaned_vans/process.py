from kafka import KafkaConsumer, KafkaProducer
import json

KAFKA_BROKER = "kafka:9092"
RAW_TOPIC = "van_raw"
PROCESSED_TOPIC = "van"


def process_van_raw_to_van_format(data):
    transformed_data = {
        "van_id": data["id"],
        "type": "van",
        "location": {
            "lat": data["position"]["latitude"],
            "lon": data["position"]["longitude"]
        },
        "timestamp": data["timestamp"]
    }
    return transformed_data


def main(producer, consumer):
    print(f"Listening to topic: {RAW_TOPIC}")
    for data in consumer:
        try:
            raw_data = data.value
            print(f"Received data: {raw_data}")

            transformed_data = process_van_raw_to_van_format(raw_data)
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
    group_id='van_processor_group'
)

# Configurar o produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print('start')
main(producer, consumer)
