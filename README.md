# Smart Mobility Streaming Platform

A modern event-driven data platform for smart mobility and real-time transportation analytics.

This project is evolving from an initial ELK + Kafka prototype into a more modular streaming architecture centered on NiFi-driven ingestion, Kafka as the event backbone, Elasticsearch for search and analytics, and observability components for operational visibility.

## Why this project exists

Urban mobility systems generate heterogeneous, time-sensitive data from transit feeds, edge devices, and operational control systems.  
This platform is designed to ingest, normalize, enrich, index, and monitor those streams in a way that is modular, observable, and extensible.

The goal is not only to visualize transportation events, but to provide an architectural foundation for near real-time smart-city data processing.

## Architecture Overview
Source of truth: `docs/architecture/overview.d2`
![Architectural Structure](https://github.com/Lucas-Armand/ELF-Kafka-Docker-BusStops-SmartCity-DashBoard/blob/main/doc/architecture/overview.png)

At a high level, the platform is organized into five architectural layers:

1. **Ingestion Layer**  
   NiFi orchestrates polling, retries, throttling, routing, and dead-letter handling for external transit and smart-city feeds.

2. **Streaming Backbone**  
   Kafka is the central event bus. Data is organized into staged topic families such as:
   - `raw.*`
   - `normalized.*`
   - `enriched.*`
   - `kpi.*`
   - `dlq.*`
   - `ref.*`

3. **Processing Services**  
   Dedicated services handle normalization, validation, enrichment, and KPI-oriented stream or batch processing.

4. **Search and Analytics Layer**  
   Kafka events can be indexed into Elasticsearch through Logstash and explored in Kibana.

5. **Observability and Control Plane**  
   Prometheus, Grafana, alerting components, and optional OpenTelemetry integration support operational monitoring.  
   Reference and access-control data can be managed through a SQL control plane and propagated through CDC patterns.

## Architectural Principles

This project is being shaped by a few core architectural principles:

- **Separation of concerns**: ingestion, transport, processing, indexing, and monitoring are decoupled
- **Event-first design**: Kafka acts as the contract boundary between stages
- **Progressive enrichment**: data becomes more valuable as it moves from raw to normalized to enriched forms
- **Operational resilience**: retries, DLQs, and observability are first-class concerns
- **Extensibility**: new feeds and processors should be added without redesigning the whole platform

## End-to-End Data Flow

A typical flow looks like this:

1. NiFi polls or receives external mobility data
2. Raw events are published into Kafka
3. Processing services consume and normalize the payloads
4. Enrichment services combine event streams with reference data
5. Search-oriented streams are indexed into Elasticsearch
6. Kibana dashboards and monitoring tools expose system and business visibility

## Current Repository Layout

```text
.
├── infra/
│   ├── compose/
│   ├── config-nifi-pipes/
│   ├── config_elastic/
│   ├── config_kafka/
│   ├── config_kibana/
│   ├── logstash/
│   ├── nifi/
│   └── prometheus/
├── services/
│   └── normalizer-gtfsrt/
├── legacy/
├── doc/
└── README.md
```


## Running the platform

The repository is organized as a modular Docker-based platform. The root Compose file includes three layers: a **base infrastructure stack**, an **application/services stack**, and an **observability stack**. The base stack brings up Kafka, Kafka UI, Elasticsearch, Kibana, NiFi, and bootstrap jobs; the apps stack currently builds the `normalizer-gtfsrt` service; and the observability stack adds Prometheus and Grafana. The repository also includes a root `.env` file, and Elasticsearch data is mounted to `/mnt/docker-volumes/elastic_data`. ([GitHub][1])

Before starting the platform, make sure the Elasticsearch data directory exists:

```bash
sudo mkdir -p /mnt/docker-volumes/elastic_data
sudo chown -R 1000:1000 /mnt/docker-volumes/elastic_data
sudo chmod -R 777 /mnt/docker-volumes/elastic_data
```

Then start the full platform from the repository root:

```bash
docker compose up -d --build
```

To inspect bootstrap jobs during the first run:

```bash
docker compose logs -f init-config-kafka
docker compose logs -f init-config-elastic
docker compose logs -f init-config-kibana
docker compose logs -f init-config-nifi-pipes
```

### Main interfaces

Once the platform is running, the main interfaces are:

* **Kafka UI**: `http://localhost:8080`
* **NiFi**: `https://localhost:8443`
* **Kibana**: `http://localhost:54321`
* **Elasticsearch**: `https://localhost:9200`
* **Prometheus**: `http://localhost:9090`
* **Grafana**: `http://localhost:3000`

NiFi uses the credentials defined by `NIFI_USERNAME` and `NIFI_PASSWORD` in the environment. Kibana connects to Elasticsearch using the Elastic credentials configured during bootstrap, and Grafana is currently configured with `admin / admin`.

If you also use **Portainer** for container administration, document it as an **optional local interface**, not as a core platform component. In the current repository structure, Portainer is not defined in the active compose files; it only appears in the older setup instructions as a separate `docker run` command exposing port `54323`. 

### Where to modify the project to add a new pipeline

To add a new ingestion pipeline, the main entry point is the NiFi pipeline/bootstrap layer under `infra/config-nifi-pipes/`. That folder already contains bootstrap code such as `common.py`, `config.py`, and `create_pipe_vehicle_positions.py`, and the NiFi area also includes `infra/nifi/pipelines/pipelines.yaml`, which already describes STM vehicle positions and trip updates flows.

A typical extension flow is:

* Add or adapt the **NiFi bootstrap/pipeline definition** in `infra/config-nifi-pipes/` and, if needed, in `infra/nifi/pipelines/`.
* Register or align the **Kafka topics** in `infra/config_kafka/kafka_config.py`.
* If the raw payload needs protobuf decoding, validation, reshaping, or contract normalization, add or extend a **normalization service** under `services/`, and register it in `infra/compose/docker-compose.apps.yml`.
* If the processed data should be searchable in Elasticsearch, update `infra/logstash/logstash.conf`.
* If the indexed document structure changes, update Elasticsearch mappings/templates in `infra/config_elastic/configure.sh`.
* If Kibana data views or saved objects need to change, update `infra/config_kibana/configure.sh` and the exported `.ndjson` objects.

### Current implementation notes

At the moment, the repository already has the pieces for a pipeline lifecycle: NiFi bootstrap creates STM GTFS-RT ingestion into Kafka, the `normalizer-gtfsrt` service consumes raw GTFS-RT topics and republishes normalized topics, Logstash consumes a normalized topic and pushes documents into Elasticsearch, and Kibana bootstrap creates data views and optionally imports saved objects.

### Recommended rule of thumb for new data sources

For each new source, think in four stages:

1. **Ingest** in NiFi
2. **Normalize** in a dedicated service if the payload is complex
3. **Index** through Logstash if the data needs search/analytics
4. **Expose** in Kibana/Grafana only after the contract is stable

That keeps ingestion, transformation, and analytics concerns separated, which is already the architectural direction suggested by your current folder layout and compose split. 

# Warning
The platform is under active evolution, and some topic/version names are still being aligned across bootstrap, processing, and indexing components.
