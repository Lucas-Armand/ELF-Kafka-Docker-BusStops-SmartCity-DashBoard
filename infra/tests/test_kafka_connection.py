from kafka import KafkaProducer, KafkaConsumer

# Configurações
bootstrap_servers = 'localhost:29092'
topic = 'raw.stm.gtfsrt.vehicle_positions.v1'

# Teste de envio (Producer)
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# Envia uma mensagem de teste
producer.send(topic, b'Teste de conexao do Kafka')
producer.flush()
print("Mensagem enviada com sucesso!")

# Teste de recebimento (Consumer)
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',
    consumer_timeout_ms=5000  # para não travar se não houver mensagem
)

print("Mensagens no tópico:")
for msg in consumer:
    print(msg.value.decode())
