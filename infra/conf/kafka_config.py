from kafka.admin import KafkaAdminClient, NewTopic

# Kafka admin setup
admin = KafkaAdminClient(
    bootstrap_servers='kafka:19092',
)
topics_list = admin.list_topics()

topics = [
    # NiFi publica (raw.*) — definido em infra/nifi/pipelines/pipelines.yaml
    "raw.stm.gtfsrt.vehicle_positions.v2",
    "raw.stm.gtfsrt.trip_updates.v2",

    # normalizer publica (contrato interno)
    "normalized.stm.gtfsrt.vehicle_positions.v2",
    "normalized.stm.getsfrt.trip_updates.v2",

    # enricher publica (joins com SQL / device registry / ACL)
    "enriched.stm.getsfrt.vehicle_positions.v2",
    "enriched.stm.getsfrt.trip_updates.v2",

    # batch/stream processors publicam (KPIs por janela / agregados)
    "kpi.stm.getsfrt.vehicle_positions.v1",
    "kpi.stm.getsfrt.trip_updates.v1",

    # DLQs (falhas no NiFi / parsing pesado no normalizer)
    "dlq.stm.gtfsrt.nifi.v1",
    "dlq.stm.gtfsrt.normalizer.v1"
    ]

for topic in topics:
    if topic not in topics_list:
        topics = [NewTopic(name=topic, num_partitions=2, replication_factor=1)]
        admin.create_topics(new_topics=topics, validate_only=False)

    else:
        print(topics_list)
