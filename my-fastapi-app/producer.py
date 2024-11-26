import json
from fastapi import FastAPI
from kafka import KafkaProducer
from datetime import datetime

KAFKA_BROKER = "kafka:9092"

app = FastAPI()

## Config Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

   
# Function to save events in a text file
def save_to_file(data, file_path="vehicle_positions.txt"):
    with open(file_path, "a") as file:
        file.write(f"{datetime.now()} - {data}\n")
    print(f"Saved to {file_path}: {data}")


@app.post("/bus_update")
async def produce_event(event: dict):
    print(f"Attempting to publish message: {event}")
    
    try:
        producer.send('bus_raw', value=event)
        producer.flush()
        print("Message successfully published")
    except Exception as e:
        print(f"Failed to publish message: {e}")
    
    return {"status": "Message attempted"}


@app.post("/stop_update")
async def stop_update(event: dict):
    print(f"Attempting to publish message: {event}")
    
    try:
        producer.send('stop_raw', value=event)
        producer.flush()
        print("Message successfully published")
    except Exception as e:
        print(f"Failed to publish message: {e}")
    
    return {"status": "Message attempted"}


@app.post("/van_update")
async def van_update(event: dict):
    print(f"Attempting to publish message: {event}")
    
    try:
        producer.send('van_raw', value=event)
        producer.flush()
        print("Message successfully published")
    except Exception as e:
        print(f"Failed to publish message: {e}")
    
    return {"status": "Message attempted"}
