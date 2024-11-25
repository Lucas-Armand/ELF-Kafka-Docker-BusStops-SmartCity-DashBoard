import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
from stm_key import STM_KEY


# URLs
url_kafka = "http://my-fastapi-app:8000/bus_update"
url_stm = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions"

headers = {
    "accept": "application/x-protobuf",
    "apiKey": STM_KEY
}


def get_vehicle_positions(url_stm):
    response = requests.get(url_stm, headers=headers)
    print(response)

    if response.status_code == 200:
        with open("vehicle_positions.pb", "wb") as f:
            f.write(response.content)
        print("Arquivo salvo com sucesso!")
    else:
        print(f"Erro ao acessar a API: {response.status_code}")


def test_fastapi_produce(url, payload):
    try:
        response = requests.post(url, json=payload)

        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        print("Resposta da API:", response.json())
        print("Teste concluído com sucesso!")
    except Exception as e:
        print(f"Erro ao testar o endpoint: {e}")


def process_vehicle_postions(url_kafka):
    # Carregue o arquivo Protobuf
    feed = gtfs_realtime_pb2.FeedMessage()
    with open("vehicle_positions.pb", "rb") as f:
        feed.ParseFromString(f.read())

    # Itere pelos dados e os transforme em algo legível
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            payload = MessageToDict(entity.vehicle)
            test_fastapi_produce(url_kafka, payload)


get_vehicle_positions(url_stm)
process_vehicle_postions(url_kafka)



