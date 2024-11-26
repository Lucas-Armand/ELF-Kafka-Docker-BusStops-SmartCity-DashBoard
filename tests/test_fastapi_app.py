import requests

# URL da API FastAPI
urls = [
    "http://my-fastapi-app:8000/bus_update",
    "http://my-fastapi-app:8000/stop_update",
    "http://my-fastapi-app:8000/van_update"
]
# Payload para a requisição
payloads = [
    {
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
    },
    {
      "stop_id": "1",
      "stop_lat": 45.42888,
      "stop_lon": -73.59883,
      "passenger_count": 20,
      "timestamp": "2024-11-25T15:00:00Z",
      "temperature": -2,
      "weather": "Rain",
      "waiting_size": 0,
      "percentile_waiting_size": 100,
      "flood_detected": False,
      "expected_wait_time_next_bus": 2
    },
    {
      "id": "1",
      "position": {"latitude": 45.42898, "longitude": -73.59883},
      "timestamp": "2024-11-25T15:00:00Z"
    }
]


def test_fastapi_produce(url, payload):
    """Testa o endpoint POST /produce"""
    try:
        # Send the POST request
        response = requests.post(url, json=payload)
        
        # Check if the response is 200 OK
        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        print("Resposta da API:", response.json())
        print("Teste concluído com sucesso!")
    except Exception as e:
        print(f"Erro ao testar o endpoint: {e}")

for i in range(3):
    test_fastapi_produce(urls[i], payloads[i])

