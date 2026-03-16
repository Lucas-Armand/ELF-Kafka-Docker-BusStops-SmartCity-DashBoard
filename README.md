# BusPas Smart Mobility Streaming Platform

A modern event-driven data platform for smart mobility and real-time transportation analytics.

This project is evolving from an initial ELK + Kafka prototype into a more modular streaming architecture centered on NiFi-driven ingestion, Kafka as the event backbone, Elasticsearch for search and analytics, and observability components for operational visibility.

## Why this project exists

Urban mobility systems generate heterogeneous, time-sensitive data from transit feeds, edge devices, and operational control systems.  
This platform is designed to ingest, normalize, enrich, index, and monitor those streams in a way that is modular, observable, and extensible.

The goal is not only to visualize transportation events, but to provide an architectural foundation for near real-time smart-city data processing.

## Architecture Overview
Source of truth: `docs/architecture/overview.d2`
![Architectural Structure](docs/architecture/overview.png)

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
