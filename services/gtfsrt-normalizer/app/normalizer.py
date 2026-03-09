import base64
import json
from typing import Any

from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2


def parse_feed_message(raw_bytes: bytes) -> gtfs_realtime_pb2.FeedMessage:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw_bytes)
    return feed


def build_feed_metadata(feed: gtfs_realtime_pb2.FeedMessage) -> dict[str, Any]:
    header = MessageToDict(
        feed.header,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
        always_print_fields_with_no_presence=False,
    )
    return {
        "gtfs_realtime_version": header.get("gtfs_realtime_version"),
        "incrementality": header.get("incrementality"),
        "timestamp": header.get("timestamp"),
    }


def vehicle_entities_to_messages(
    feed: gtfs_realtime_pb2.FeedMessage,
    source_topic: str,
    source_partition: int,
    source_offset: int,
) -> list[dict[str, Any]]:
    feed_meta = build_feed_metadata(feed)
    messages: list[dict[str, Any]] = []

    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue

        vehicle_payload = MessageToDict(
            entity.vehicle,
            preserving_proto_field_name=True,
            use_integers_for_enums=False,
            always_print_fields_with_no_presence=False,
        )

        messages.append(
            {
                "schema_version": "v1",
                "source": {
                    "topic": source_topic,
                    "partition": source_partition,
                    "offset": source_offset,
                },
                "feed": feed_meta,
                "entity_id": entity.id,
                "entity_type": "vehicle_position",
                "payload": vehicle_payload,
            }
        )

    return messages


def trip_update_entities_to_messages(
    feed: gtfs_realtime_pb2.FeedMessage,
    source_topic: str,
    source_partition: int,
    source_offset: int,
) -> list[dict[str, Any]]:
    feed_meta = build_feed_metadata(feed)
    messages: list[dict[str, Any]] = []

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        trip_update_payload = MessageToDict(
            entity.trip_update,
            preserving_proto_field_name=True,
            use_integers_for_enums=False,
            always_print_fields_with_no_presence=False,
        )

        messages.append(
            {
                "schema_version": "v1",
                "source": {
                    "topic": source_topic,
                    "partition": source_partition,
                    "offset": source_offset,
                },
                "feed": feed_meta,
                "entity_id": entity.id,
                "entity_type": "trip_update",
                "payload": trip_update_payload,
            }
        )

    return messages


def build_dlq_message(
    raw_bytes: bytes,
    source_topic: str,
    source_partition: int,
    source_offset: int,
    error: Exception,
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "source": {
            "topic": source_topic,
            "partition": source_partition,
            "offset": source_offset,
        },
        "error_type": type(error).__name__,
        "error_message": str(error),
        "raw_base64": base64.b64encode(raw_bytes).decode("utf-8"),
    }


def json_dumps(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
