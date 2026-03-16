from common import NiFiClient, create_http_to_kafka_pipeline
from config import (
    KAFKA_BOOTSTRAP,
    NIFI_PASSWORD,
    NIFI_ROOT_PG_ID,
    NIFI_URL,
    NIFI_USERNAME,
    NIFI_VERIFY_SSL,
    RAW_VEHICLE_POSITIONS_TOPIC,
    STM_API_KEY,
    STM_VEHICLE_POSITIONS_URL,
    DLQ_STM_NIFI_TOPIC,
)


def main():
    client = NiFiClient(
        base_url=NIFI_URL,
        username=NIFI_USERNAME,
        password=NIFI_PASSWORD,
        verify_ssl=NIFI_VERIFY_SSL,
    )
    client.wait_until_ready()

    process_group = create_http_to_kafka_pipeline(
        client=client,
        parent_pg_id=NIFI_ROOT_PG_ID,
        process_group_name="STM GTFS-RT Vehicle Positions",
        remote_url=STM_VEHICLE_POSITIONS_URL,
        kafka_topic_raw=RAW_VEHICLE_POSITIONS_TOPIC,
        kafka_topic_dlq=DLQ_STM_NIFI_TOPIC,
        kafka_bootstrap=KAFKA_BOOTSTRAP,
        api_key=STM_API_KEY,
    )

    print("Vehicle positions pipeline created successfully.")
    print(f"Process Group ID: {process_group['id']}")


if __name__ == "__main__":
    main()
