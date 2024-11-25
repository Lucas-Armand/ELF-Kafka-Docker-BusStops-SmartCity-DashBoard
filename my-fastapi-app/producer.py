import json
from fastapi import FastAPI
from pydantic import BaseModel, Field
from kafka import KafkaProducer
from datetime import datetime


KAFKA_BROKER = "kafka:9092"
TOPIC = "bus_raw"

app = FastAPI()


## Configurar o produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


class Trip(BaseModel):
    trip_id: str = Field(alias="tripId")
    start_time: str = Field(alias="startTime")
    start_date: str = Field(alias="startDate")
    route_id: str = Field(alias="routeId")


class Position(BaseModel):
    latitude: float
    longitude: float
    speed: float


class Vehicle(BaseModel):
    id: str


class VehiclePosition(BaseModel):
    vehicle: Vehicle
    trip: Trip
    position: Position
    current_stop_sequence: int = Field(alias="currentStopSequence")
    current_status: str = Field(alias="currentStatus")
    timestamp: int
    occupancy_status: str = Field(alias="occupancyStatus")


# Função para salvar os eventos em um arquivo de texto
def save_to_file(data, file_path="vehicle_positions.txt"):
    with open(file_path, "a") as file:
        file.write(f"{datetime.now()} - {data}\n")
    print(f"Saved to {file_path}: {data}")


@app.post("/bus_update")
async def produce_event(event: VehiclePosition):
    message = event.dict()
    print(f"Attempting to publish message: {message}")
    
    try:
        producer.send(TOPIC, value=message)
        producer.flush()
        print("Message successfully published")
    except Exception as e:
        print(f"Failed to publish message: {e}")
    
    return {"status": "Message attempted"}

