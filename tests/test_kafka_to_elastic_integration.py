
from kafka import KafkaProducer
from elasticsearch import Elasticsearch
import time
        
KAFKA_BROKER = "kafka:9092"
ELASTIC_HOST = "http://elasticsearch:9200"
TOPIC = "bus"
INDEX_NAME = "bus"
    
    # Configurar o produtor Kafka
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

# Mensagem de teste
test_message = {
    "bus_id": "TEST_BUS",
    "location": {"lat": 45.5017, "lon": -73.5673},
    "timestamp": "2024-11-23T10:00:00Z",
    "event_type":"bus"
}

producer.send(TOPIC, value=str(test_message).encode("utf-8"))
producer.flush()
print(f"Mensagem enviada para o tópico Kafka: {TOPIC}")

# Esperar que o Logstash processe a mensagem
time.sleep(10)  # Aguarde alguns segundos para que a mensagem seja processada

# Verificar no Elasticsearch
es = Elasticsearch(ELASTIC_HOST)
result = es.search(index=INDEX_NAME, query={"match": {"bus_id": "TEST_BUS"}})
hits = result["hits"]["hits"]

if hits:
    print(f"Mensagem encontrada no Elasticsearch: {hits[0]['_source']}")
else:
    print("Mensagem NÃO encontrada no Elasticsearch. Verifique o Logstash.")
es.transport.close()

