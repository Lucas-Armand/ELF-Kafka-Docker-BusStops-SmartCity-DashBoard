import logging
import signal
import base64
import binascii

from kafka import KafkaConsumer, KafkaProducer

from config import (
    DLQ_TOPIC,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    NORMALIZED_TRIP_UPDATES_TOPIC,
    NORMALIZED_VEHICLE_POSITIONS_TOPIC,
    RAW_TRIP_UPDATES_TOPIC,
    RAW_VEHICLE_POSITIONS_TOPIC,
)

from kafka_utils import create_consumer, create_producer, ensure_topics

from normalizer import (
    build_dlq_message,
    json_dumps,
    parse_feed_message,
    trip_update_entities_to_messages,
    vehicle_entities_to_messages,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("stm-gtfsrt-normalizer")

RUNNING = True

def handle_stop_signal(signum, frame):
    global RUNNING
    logger.info("Received signal %s, stopping...", signum)
    RUNNING = False

def normalize_message(message):
    feed = parse_feed_message(message.value)

    if message.topic == RAW_VEHICLE_POSITIONS_TOPIC:
        normalized_messages = vehicle_entities_to_messages(
            feed=feed,
            source_topic=message.topic,
            source_partition=message.partition,
            source_offset=message.offset,
        )
        destination_topic = NORMALIZED_VEHICLE_POSITIONS_TOPIC

    elif message.topic == RAW_TRIP_UPDATES_TOPIC:
        normalized_messages = trip_update_entities_to_messages(
            feed=feed,
            source_topic=message.topic,
            source_partition=message.partition,
            source_offset=message.offset,
        )
        destination_topic = NORMALIZED_TRIP_UPDATES_TOPIC

    else:
        raise ValueError(f"Unsupported topic: {message.topic}")

    return destination_topic, normalized_messages


def publish_normalized(producer, destination_topic, message, normalized_messages):
    for idx, payload in enumerate(normalized_messages):
        producer.send(
            destination_topic,
            key=f"{message.topic}:{message.partition}:{message.offset}:{idx}",
            value=json_dumps(payload),
        )
    producer.flush()


def publish_to_dlq(producer, message, exc):
    dlq_payload = build_dlq_message(
        raw_bytes=message.value,
        source_topic=message.topic,
        source_partition=message.partition,
        source_offset=message.offset,
        error=exc,
    )

    producer.send(
        DLQ_TOPIC,
        key=f"dlq:{message.topic}:{message.partition}:{message.offset}",
        value=json_dumps(dlq_payload),
    )
    producer.flush()


def payload_debug_info(raw_bytes, preview_len=64):
    if raw_bytes is None:
        return {
            "size_bytes": 0,
            "hex_preview": "",
            "base64_preview": "",
            "text_preview": "",
        }

    preview = raw_bytes[:preview_len]

    try:
        text_preview = preview.decode("utf-8", errors="replace")
    except Exception:
        text_preview = ""

    return {
        "size_bytes": len(raw_bytes),
        "hex_preview": binascii.hexlify(preview).decode("ascii"),
        "base64_preview": base64.b64encode(preview).decode("ascii"),
        "text_preview": text_preview,
    }

def main():
    ensure_topics(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        topics=[
            RAW_VEHICLE_POSITIONS_TOPIC,
            RAW_TRIP_UPDATES_TOPIC,
            NORMALIZED_VEHICLE_POSITIONS_TOPIC,
            NORMALIZED_TRIP_UPDATES_TOPIC,
            DLQ_TOPIC,
        ],
    )

    consumer = create_consumer()
    producer = create_producer()

    signal.signal(signal.SIGINT, handle_stop_signal)
    signal.signal(signal.SIGTERM, handle_stop_signal)

    logger.info(
        "Starting normalizer. Consuming from %s, %s",
        RAW_VEHICLE_POSITIONS_TOPIC,
        RAW_TRIP_UPDATES_TOPIC,
    )

    try:
        while RUNNING:
            batches = consumer.poll(timeout_ms=1000)

            if not batches:
                continue

            for _, records in batches.items():
                for message in records:
                    try:
                        destination_topic, normalized_messages = normalize_message(message)
                        publish_normalized(
                            producer,
                            destination_topic,
                            message,
                            normalized_messages,
                        )
                        consumer.commit()

                        logger.info(
                            "Processed topic=%s partition=%s offset=%s -> %s messages to %s",
                            message.topic,
                            message.partition,
                            message.offset,
                            len(normalized_messages),
                            destination_topic,
                        )

                    except Exception as exc:
                        debug = payload_debug_info(message.value)

                        logger.exception(
                            (
                                "Failed processing "
                                "topic=%s partition=%s offset=%s key=%r "
                                "size_bytes=%s hex_preview=%s base64_preview=%s text_preview=%r"
                            ),
                            message.topic,
                            message.partition,
                            message.offset,
                            message.key,
                            debug["size_bytes"],
                            debug["hex_preview"],
                            debug["base64_preview"],
                            debug["text_preview"],
                        )

                        publish_to_dlq(producer, message, exc)
                        consumer.commit()

    finally:
        consumer.close()
        producer.close()
        logger.info("Normalizer stopped.")


if __name__ == "__main__":
    main()
