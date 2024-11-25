import requests

# URL da API FastAPI
url = "http://my-fastapi-app:8000/bus_update"

# Payload para a requisição
payload = {
    "id": "41031",
    "vehicle": {"id": "41031"},
    "trip": {
        "trip_id": "280062452",
        "start_time": "00:01:00",
        "start_date": "20241124",
        "route_id": "97"
    },
    "position": {
        "latitude": 45.5425949,
        "longitude": -73.5617142,
        "speed": 0
    },
    "current_stop_sequence": 25,
    "current_status": "STOPPED_AT",
    "timestamp": 1732426173,
    "occupancy_status": "FEW_SEATS_AVAILABLE"
}


def test_fastapi_produce(url, payload):
    """Testa o endpoint POST /produce"""
    try:
        # Envia a requisição POST
        response = requests.post(url, json=payload)
        
        # Verifica se a resposta é 200 OK
        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        print("Resposta da API:", response.json())
        print("Teste concluído com sucesso!")
    except Exception as e:
        print(f"Erro ao testar o endpoint: {e}")


test_fastapi_produce(url, payload)

