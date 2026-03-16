from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    RAW_TRIP_UPDATES_TOPIC,
    RAW_VEHICLE_POSITIONS_TOPIC,
)


def ensure_topics(bootstrap_servers, topics, partitions=2):
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    existing_topics = set(admin.list_topics())

    to_create = [
        NewTopic(name=topic, num_partitions=partitions, replication_factor=1)
        for topic in topics
        if topic not in existing_topics
    ]

    if not to_create:
        admin.close()
        return

    try:
        admin.create_topics(new_topics=to_create, validate_only=False)
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def create_consumer():
    return KafkaConsumer(
        RAW_VEHICLE_POSITIONS_TOPIC,
        RAW_TRIP_UPDATES_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda x: x,
        key_deserializer=lambda x: x,
        max_poll_records=100,
    )


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: x,
        key_serializer=lambda x: x.encode("utf-8") if isinstance(x, str) else x,
        acks="all",
        retries=10,
    )
