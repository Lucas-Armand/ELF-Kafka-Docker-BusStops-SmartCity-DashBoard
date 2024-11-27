import requests
import pandas as pd
import numpy as np

np.random.seed(42)

def mock_data(df):
    # Generate a random temperature for each stop
    # stops in north are colder:
    lat_min = np.min(df['stop_lat'])
    lat_max = np.max(df['stop_lat'])

    df['temp_mean'] = np.interp(df['stop_lat'], [lat_min, lat_max], [-1, -5])
    df['temperature'] = np.random.normal(df['temp_mean'], 0.3)

    df = df.drop(columns=['temp_mean'])

    # Generate weather in the point
    df['weather'] = np.random.choice(['Rain', 'Snow', 'Strong Rain'], size=len(df), p=[0.6, 0.2, 0.2])

    # Generate the number of persons wainting
    df['waiting_size'] = np.random.exponential(scale=4, size=len(df)).astype(int)

    # Generate the number of persons wainting
    df['percentile_waiting_size']= np.random.normal(loc=80, scale=30, size=len(df))

    # Add flood detected
    random_row = np.random.randint(0, len(df))
    df['flood_detected'] = False
    df.loc[random_row, 'flood_detected'] = True
    df.loc[random_row, 'weather'] = 'Strong Rain'

    # Add expected wait time to next bus
    df['expected_wait_time_next_bus'] = np.random.normal(loc=5, scale=5, size=len(df))
    
    # Generate the number of persons wainting
    df['waiting_size'] = np.random.exponential(scale=0.4, size=len(df)).astype(int)

    return df


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


df_stop = pd.read_csv('./stops.txt')
df_stop = mock_data(df_stop)
df_stop = df_stop.drop(columns=['stop_url', 'parent_station'])

# URL da API FastAPI
url = "http://my-fastapi-app:8000/stop_update"

for i, x in df_stop.iterrows():
    print(x.to_dict())
    test_fastapi_produce(url, x.to_dict())


