from kafka import KafkaProducer
from elasticsearch import Elasticsearch
import time
import json

KAFKA_BROKER = "kafka:9092"
ELASTIC_HOST = "http://elasticsearch:9200"


# Dados de exemplo organizados por tópico
data_samples = {
    "bus": [
        {"bus_id": "B001", "event_type": "bus", "location": {"lat": 45.5017, "lon": -73.5673}, "timestamp": "2024-11-18T10:00:00Z"},
        {"bus_id": "B002", "event_type": "bus", "location": {"lat": 45.5020, "lon": -73.5676}, "timestamp": "2024-11-18T10:01:00Z"},
        {"bus_id": "B003", "event_type": "bus", "location": {"lat": 45.5030, "lon": -73.5680}, "timestamp": "2024-11-18T10:02:00Z"},
        {"bus_id": "B004", "event_type": "bus", "location": {"lat": 45.5040, "lon": -73.5690}, "timestamp": "2024-11-18T10:03:00Z"},
        {"bus_id": "B005", "event_type": "bus", "location": {"lat": 45.5050, "lon": -73.5700}, "timestamp": "2024-11-18T10:04:00Z"},
        {"bus_id": "B006", "event_type": "bus", "location": {"lat": 45.5060, "lon": -73.5710}, "timestamp": "2024-11-18T10:05:00Z"},
        {"bus_id": "B007", "event_type": "bus", "location": {"lat": 45.5070, "lon": -73.5720}, "timestamp": "2024-11-18T10:06:00Z"},
        {"bus_id": "B008", "event_type": "bus", "location": {"lat": 45.5080, "lon": -73.5730}, "timestamp": "2024-11-18T10:07:00Z"},
        {"bus_id": "B009", "event_type": "bus", "location": {"lat": 45.5090, "lon": -73.5740}, "timestamp": "2024-11-18T10:08:00Z"},
        {"bus_id": "B010", "event_type": "bus", "location": {"lat": 45.5100, "lon": -73.5750}, "timestamp": "2024-11-18T10:09:00Z"}
    ],
    "van": [
        {"van_id": "V001", "event_type": "van", "location": {"lat": 45.5200, "lon": -73.5500}, "timestamp": "2024-11-18T10:00:00Z"},
        {"van_id": "V002", "event_type": "van", "location": {"lat": 45.5210, "lon": -73.5510}, "timestamp": "2024-11-18T10:01:00Z"},
        {"van_id": "V003", "event_type": "van", "location": {"lat": 45.5220, "lon": -73.5520}, "timestamp": "2024-11-18T10:02:00Z"},
        {"van_id": "V004", "event_type": "van", "location": {"lat": 45.5230, "lon": -73.5530}, "timestamp": "2024-11-18T10:03:00Z"},
        {"van_id": "V005", "event_type": "van", "location": {"lat": 45.5240, "lon": -73.5540}, "timestamp": "2024-11-18T10:04:00Z"},
        {"van_id": "V006", "event_type": "van", "location": {"lat": 45.5250, "lon": -73.5550}, "timestamp": "2024-11-18T10:05:00Z"},
        {"van_id": "V007", "event_type": "van", "location": {"lat": 45.5260, "lon": -73.5560}, "timestamp": "2024-11-18T10:06:00Z"},
        {"van_id": "V008", "event_type": "van", "location": {"lat": 45.5270, "lon": -73.5570}, "timestamp": "2024-11-18T10:07:00Z"},
        {"van_id": "V009", "event_type": "van", "location": {"lat": 45.5280, "lon": -73.5580}, "timestamp": "2024-11-18T10:08:00Z"},
        {"van_id": "V010", "event_type": "van", "location": {"lat": 45.5290, "lon": -73.5590}, "timestamp": "2024-11-18T10:09:00Z"}
    ],
    "weather": [
        {"event_type": "weather_station", "location": {"lat": 45.5017, "lon": -73.5673}, "temp": -5, "precipitation": "snow", "timestamp": "2024-11-18T10:00:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5020, "lon": -73.5676}, "temp": -4, "precipitation": "snow", "timestamp": "2024-11-18T10:01:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5030, "lon": -73.5680}, "temp": -6, "precipitation": "rain", "timestamp": "2024-11-18T10:02:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5040, "lon": -73.5690}, "temp": -7, "precipitation": "rain", "timestamp": "2024-11-18T10:03:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5050, "lon": -73.5700}, "temp": -3, "precipitation": "snow", "timestamp": "2024-11-18T10:04:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5060, "lon": -73.5710}, "temp": -2, "precipitation": "clear", "timestamp": "2024-11-18T10:05:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5070, "lon": -73.5720}, "temp": -1, "precipitation": "clear", "timestamp": "2024-11-18T10:06:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5080, "lon": -73.5730}, "temp": -3, "precipitation": "rain", "timestamp": "2024-11-18T10:07:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5090, "lon": -73.5740}, "temp": -4, "precipitation": "rain", "timestamp": "2024-11-18T10:08:00Z"},
        {"event_type": "weather_station", "location": {"lat": 45.5100, "lon": -73.5750}, "temp": -5, "precipitation": "snow", "timestamp": "2024-11-18T10:09:00Z"}
    ]
}

# Configurar o produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Enviar mensagens para os tópicos do Kafka
for topic, messages in data_samples.items():
    for message in messages:
        producer.send(topic, value=message)
        print(f"Mensagem enviada para o tópico {topic}: {message}")

producer.flush()
print("Todas as mensagens foram enviadas para o Kafka.")
