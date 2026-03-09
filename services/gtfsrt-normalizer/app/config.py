import os

KAFKA_BOOTSTRAP_SERVERS = [
    x.strip() for x in os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:19092").split(",") if x.strip()
]
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "stm-gtfsrt-normalizer-v1")

RAW_VEHICLE_POSITIONS_TOPIC = os.getenv(
    "RAW_VEHICLE_POSITIONS_TOPIC",
    "raw.stm.gtfsrt.vehicle_positions.v1",
)
RAW_TRIP_UPDATES_TOPIC = os.getenv(
    "RAW_TRIP_UPDATES_TOPIC",
    "raw.stm.gtfsrt.trip_updates.v1",
)

NORMALIZED_VEHICLE_POSITIONS_TOPIC = os.getenv(
    "NORMALIZED_VEHICLE_POSITIONS_TOPIC",
    "normalized.stm.gtfsrt.vehicle_positions.v1",
)
NORMALIZED_TRIP_UPDATES_TOPIC = os.getenv(
    "NORMALIZED_TRIP_UPDATES_TOPIC",
    "normalized.stm.gtfsrt.trip_updates.v1",
)

DLQ_TOPIC = os.getenv("DLQ_TOPIC", "dlq.stm.gtfsrt.normalizer.v1")
