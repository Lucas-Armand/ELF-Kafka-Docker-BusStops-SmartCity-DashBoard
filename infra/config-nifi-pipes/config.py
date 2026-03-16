import os

NIFI_URL = os.getenv("NIFI_URL", "https://nifi:8443/nifi-api")
NIFI_USERNAME = os.getenv("NIFI_USERNAME", "admin")
NIFI_PASSWORD = os.getenv("NIFI_PASSWORD", "adminadminadmin")
NIFI_VERIFY_SSL = os.getenv("NIFI_VERIFY_SSL", "false").lower() == "true"
NIFI_ROOT_PG_ID = os.getenv("NIFI_ROOT_PG_ID", "root")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:19092")

STM_VEHICLE_POSITIONS_URL = os.getenv(
    "STM_VEHICLE_POSITIONS_URL",
    "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions",
)
STM_TRIP_UPDATES_URL = os.getenv(
    "STM_TRIP_UPDATES_URL",
    "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates",
)

RAW_VEHICLE_POSITIONS_TOPIC = os.getenv(
    "RAW_VEHICLE_POSITIONS_TOPIC",
    "raw.stm.gtfsrt.vehicle_positions.v2",
)
RAW_TRIP_UPDATES_TOPIC = os.getenv(
    "RAW_TRIP_UPDATES_TOPIC",
    "raw.stm.gtfsrt.trip_updates.v2",
)

DLQ_STM_NIFI_TOPIC = os.getenv(
    "DLQ_STM_NIFI_TOPIC",
    "dlq.stm.gtfsrt.nifi.v1",
)

STM_API_KEY = os.getenv("STM_API_KEY", "")
