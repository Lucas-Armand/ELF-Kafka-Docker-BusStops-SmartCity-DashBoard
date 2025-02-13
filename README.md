# **Smart Mobility Data Processing System and DashBoard**

This is a modern data streaming, visualization, and real-time monitoring project designed for smart city solutions. It simulates a public transportation monitoring and analytics system using data from buses, vans, and smart bus stops.

This project uses Elasticsearch, Logstash, Kibana (ELK Stack), and Kafka, orchestrated with Docker, to create a scalable and modular architecture. The solution enables real-time data ingestion, processing, and visualization, providing critical insights for managing public transportation and urban mobility.


## **Architecture**
![System Architecture](https://github.com/Lucas-Armand/ELF-Kafka-Docker-BusStops-SmartCity-DashBoard/blob/main/img/architecture.png?raw=true) <!-- Replace with your architecture image -->

### **Components**
1. **FastAPI**:
   - Acts as the data producer for the Kafka topics.
   - Exposes RESTful APIs for data ingestion (`/bus_update`, `/stop_update` and `/van_update`).

2. **Apache Kafka**:
   - Middleware for real-time data streaming.
   - Handles topics like `bus_raw`, `van_raw`, `stop_raw`, `bus`, `van` and `stop`.

3. **Logstash**:
   - Consumes data from Kafka.
   - Filters and processes data before sending them to Elasticsearch.

4. **Elasticsearch**:
   - Stores processed data.
   - Provides a search and analytics engine for querying insights.

5. **Kibana/Custom Dashboard**:
   - A dashboard for visualizing actionable insights, such as delays or van service requirements.

## **Setup**
Quick Start (e.g., on a new GCP VM)

Use the following commands if you’re setting up on a fresh environment (like Google Cloud Platform, AWS EC2, etc.):

# 1. Install Git
sudo apt install -y git

# 2. Clone the Repository
git clone https://github.com/Lucas-Armand/ELF-Kafka-Docker-BusStops-SmartCity-DashBoard.git
cd ELF-Kafka-Docker-BusStops-SmartCity-DashBoard

# 3. Install Docker and Docker Compose
sudo apt update && sudo apt install -y docker.io docker-compose

# 4. Start and enable the Docker service
sudo systemctl start docker
sudo systemctl enable docker

# 5. Add your user to the Docker group (so you can run Docker commands without sudo)
sudo usermod -aG docker $USER
newgrp docker

# 6. Build and run the containers in detached mode
docker-compose up -d



## **Technologies Used**

- **Programming Language**: Python 3.9+
- **Data Streaming**: Apache Kafka
- **Data Processing**: Logstash
- **Database**: Elasticsearch
- **Visualization**: Kibana
- **API Framework**: FastAPI
- **Containerization**: Docker and Docker Compose

## **Setup**

### **Steps to Run**
1. Clone the repository:
   ```bash
   git clone https://github.com/Lucas-Armand/ELF-Kafka-Docker-BusStops-SmartCity-DashBoard.git
   cd ELF-Kafka-Docker-BusStops-SmartCity-DashBoard
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

3. Access the FastAPI Swagger UI for testing APIs:
   ```bash
   URL: http://localhost:8000/docs
   ```

4. View the processed data in Kibana:
   ```bash
   URL: http://localhost:5601
   ```

## **Tests**

### **Testing Using the `tests` Docker**

The project includes a **test** Docker container to validate each component. To use it:

1. Run the **test** container:
    ```bash
    docker-compose run test
    ```

2. Inside the container, execute individual tests:
    ```bash
    python test_<TEST_NAME>.py
    ```

    Examples:
    - `python test_fastapi_app.py`
    - `python test_elastic_storing_retrieving.py`

### **Manual Testing with `curl`**

If you prefer manual testing, use the following **curl** commands:

1. **Test Bus Data**:
    ```bash
    curl -X POST "http://localhost:8000/bus_update" \
    -H "Content-Type: application/json" \
    -d '{
       "id": "3",
       "vehicle": {"id": "3"},
       "trip": {
          "tripId": "1",
          "startTime": "00:01:00",
          "startDate": "20241124",
          "routeId": "97"
       },
       "position": {
          "latitude": 45.42878,
          "longitude": -73.59883,
          "speed": 0
       },
       "currentStopSequence": 25,
       "currentStatus": "STOPPED_AT",
       "timestamp": 1732426173,
       "occupancyStatus": "FEW_SEATS_AVAILABLE"
    }'
    ```

2. **Test Stop Data**:
    ```bash
    curl -X POST "http://localhost:8000/stop_update" \
    -H "Content-Type: application/json" \
    -d '{
       "stop_id": "1",
       "stop_lat": 45.42888,
       "stop_lon": -73.59883,
       "passenger_count": 20,
       "timestamp": "2024-11-25T15:00:00Z",
       "temperature": -2,
       "weather": "Rain",
       "waiting_size": 0,
       "percentile_waiting_size": 100,
       "flood_detected": false,
       "expected_wait_time_next_bus": 2
    }'
    ```

3. **Test Van Data**:
    ```bash
    curl -X POST "http://localhost:8000/van_update" \
    -H "Content-Type: application/json" \
    -d '{
       "id": "1",
       "position": {"latitude": 45.42898, "longitude": -73.59883},
       "timestamp": "2024-11-25T15:00:00Z",
       "type":"van"
    }'
    ```

## **References**

1. [GTFS Documentation](https://developers.google.com/transit/gtfs)
2. [Kafka Python Docs](https://kafka-python.readthedocs.io/en/master/)
3. [Logstash Documentation](https://www.elastic.co/guide/en/logstash/master/introduction.html)
4. [Elasticsearch Mappings Docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html)
5. [Kafka-Real-Time-Streaming Repository - GitHub](https://github.com/puchki2015/Kafka-Real-Time-Streaming)
6. [Kafka to Elasticsearch with Python - GitHub](https://github.com/ZianTsabit/kafka-elasticsearch-python)
7. [Elasticsearch + Logstash + Kibana  - GitHub](https://github.com/shazforiot/Elasticsearch-logstash-Kibana-Docker-Compose)  
8. [Docker ELK Stack - GitHub](https://github.com/deviantony/docker-elk)

## **Video**
### **Project Overview Video**
A 10-minute video walkthrough of the project is available, explaining the architecture, data flow, and usage. 
[![Everything Is AWESOME](https://github.com/Lucas-Armand/ELF-Kafka-Docker-BusStops-SmartCity-DashBoard/blob/main/img/video.png?raw=true)](https://youtu.be/giVNQp5ZooQ)




