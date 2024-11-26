from kafka.admin import KafkaAdminClient, NewTopic

# Kafka admin setup
admin = KafkaAdminClient(
    bootstrap_servers='kafka:9092',
)
topics_list = admin.list_topics()
# Admin logic

topics = ['bus','van','stop','bus_raw','van_raw','stop_raw']

for topic in topics:
    if topic not in topics_list:
        topics = [NewTopic(name=topic, num_partitions=2, replication_factor=1)]
        admin.create_topics(new_topics=topics, validate_only=False)

    else:
        print(topics_list)
