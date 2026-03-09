# NiFi Flow — STM GTFS-RT VehiclePositions → Kafka (`bus_raw`)

Goal:
- Replace the Python collector + FastAPI producer.
- NiFi will: pull STM feed (protobuf) → decode → explode `entity[]` → keep only `vehicle` entities → publish to Kafka.

## Prerequisites
- NiFi running at `https://localhost:8443`
- Kafka reachable at `kafka:9092` (same Docker network)
- Proto file available at `/opt/nifi/proto/gtfs-realtime.proto`

## Parameters (create a Parameter Context named: `gtfsrt_stm`)
- `STM_API_KEY` = (from your `.env`)
- `STM_VEHICLE_POSITIONS_URL` = (from your `.env`)
- `KAFKA_BOOTSTRAP_SERVERS` = `kafka:9092`
- `KAFKA_TOPIC_BUS_RAW` = `bus_raw`
- `POLL_INTERVAL_SECONDS` = e.g. `10`

## Controller Services (inside the Process Group)
1) **ProtobufReader**
   - Message Type: `transit_realtime.FeedMessage`
   - Proto Directory: `/opt/nifi/proto`
   - Schema Access Strategy: generate from proto (recommended)

   The ProtobufReader decodes binary protobuf using the `.proto` file + the message type.

2) **JsonTreeReader** (for record-oriented JSON)
   - Schema Access Strategy: Inherit Record Schema

3) **JsonRecordSetWriter** (to write JSON)
   - Output Grouping: `One Line Per Object` (recommended for Kafka)
   - Pretty Print JSON: `false`
   - Schema Access Strategy: Inherit Record Schema

4) **Kafka3ConnectionService**
   - Bootstrap Servers: `${KAFKA_BOOTSTRAP_SERVERS}`
   - Security Protocol: `PLAINTEXT` (default)

## Processors (flow order)

### A) GenerateFlowFile
- Schedule: every `${POLL_INTERVAL_SECONDS}s` (e.g. 10s)
- Custom Text: empty
- File Size: 0B  
Output → InvokeHTTP

### B) InvokeHTTP
- HTTP Method: `GET`
- Remote URL: `${STM_VEHICLE_POSITIONS_URL}`
- Add dynamic properties:
  - `accept` = `application/x-protobuf`
  - `apiKey` = `${STM_API_KEY}`

Connect:
- `Response` → `UpdateAttribute`
- `Retry / No Retry / Failure` → (DLQ or debug sink, e.g. PutFile)

Notes:
- InvokeHTTP populates attributes like `invokehttp.status.code`.
- The response body is routed through the proper relationship.

### C) UpdateAttribute (metadata)
- `gtfsrt.source` = `stm`
- `gtfsrt.feed` = `vehicle_positions`
- `gtfsrt.fetched_at` = `${now():format("yyyy-MM-dd'T'HH:mm:ss.SSSXXX")}`

### D) ForkRecord (explode `entity[]`)
- Mode: `Extract`
- Record Reader: `ProtobufReader`
- Record Writer: `JsonRecordSetWriter` (Output Grouping: Array)
- Dynamic Property (name can be anything, e.g. `entities`):
  - `entities` = `/entity`

Connect relationship `fork` → `QueryRecord`

### E) QueryRecord (keep only entities with `vehicle`)
- Record Reader: `JsonTreeReader`
- Record Writer: `JsonRecordSetWriter` (Output Grouping: Array)
- Dynamic Property:
  - `vehicles` = `SELECT * FROM FLOWFILE WHERE vehicle IS NOT NULL`

Connect:
- Relationship `vehicles` → `PublishKafka`
- `failure` → debug sink (e.g. PutFile)

### F) PublishKafka
- Kafka Connection Service: `Kafka3ConnectionService`
- Topic Name: `${KAFKA_TOPIC_BUS_RAW}`
- Record Reader: `JsonTreeReader`
- Record Writer: `JsonRecordSetWriter` (Output Grouping: One Line Per Object)
- FlowFile Attribute Header Pattern: `gtfsrt\..*`  
  (sends metadata as Kafka headers)

Result:
- Each `FeedEntity` containing `vehicle` becomes **one JSON message** in topic `bus_raw`.

## Compatibility with your previous payload
Your previous code published `MessageToDict(entity.vehicle)` (vehicle object only).

This flow publishes the full entity record (entity id + vehicle + other fields), which is usually better for traceability/debugging.

If you want to publish **only** the `vehicle` object, you can adjust `QueryRecord` to project only that field (and optionally rename columns). However, keeping the full entity is recommended.
