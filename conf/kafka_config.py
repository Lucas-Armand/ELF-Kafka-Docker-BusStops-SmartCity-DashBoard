from kafka.admin import KafkaAdminClient, NewTopic

# Kafka admin setup
admin = KafkaAdminClient(
    bootstrap_servers='kafka:9092',
)
topics_list = admin.list_topics()

topics = [
    # NiFi publica (raw.*) — definido em infra/nifi/pipelines/pipelines.yaml
    "raw.gtfsrt.vehicle_positions.v1",
    "raw.gtfsrt.trip_updates.v1",

    # normalizer publica (contrato interno)
    "normalized.vehicle_positions.v1",
    "normalized.trip_updates.v1",

    # enricher publica (joins com SQL / device registry / ACL)
    "enriched.vehicle_positions.v1",
    "enriched.trip_updates.v1",

    # batch/stream processors publicam (KPIs por janela / agregados)
    "kpi.vehicle_positions.v1",
    "kpi.trip_updates.v1",

    # DLQs (falhas no NiFi / parsing pesado no normalizer)
    "dlq.gtfsrt.nifi.v1",
    "dlq.gtfsrt.normalizer.v1"
    ]

for topic in topics:
    if topic not in topics_list:
        topics = [NewTopic(name=topic, num_partitions=2, replication_factor=1)]
        admin.create_topics(new_topics=topics, validate_only=False)

    else:
        print(topics_list)
