
from kafka import KafkaProducer
from elasticsearch import Elasticsearch
import time
        
KAFKA_BROKER = "kafka:9092"
ELASTIC_HOST = "http://elasticsearch:9200"
TOPIC = "bus"
INDEX_NAME = "bus"
    
# Send mensage direct to Kafka:
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

test_message = {
    "bus_id": "TEST_BUS",
    "location": {"lat": 45.5017, "lon": -73.5673},
    "timestamp": "2024-11-23T10:00:00Z",
    "type":"bus",
    "occupancyStatus": "FEW_SEATS_AVAILABLE"       
}

producer.send(TOPIC, value=str(test_message).encode("utf-8"))
producer.flush()
print(f"Mensagem enviada para o tópico Kafka: {TOPIC}")

# Wait for Logstash to process the message
time.sleep(10)  

# Check if the changes were reflected in the Elasticsearch database:
es = Elasticsearch(ELASTIC_HOST)
result = es.search(index=INDEX_NAME, query={"match": {"bus_id": "TEST_BUS"}})
hits = result["hits"]["hits"]

if hits:
    print(f"Mensagem encontrada no Elasticsearch: {hits[0]['_source']}")
else:
    print("Mensagem NÃO encontrada no Elasticsearch. Verifique o Logstash.")
es.transport.close()

