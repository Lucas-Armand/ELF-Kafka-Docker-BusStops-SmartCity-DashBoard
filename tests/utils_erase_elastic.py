from elasticsearch import Elasticsearch

# Configuração do Elasticsearch
ELASTIC_HOST = "http://elasticsearch:9200"

es = Elasticsearch(ELASTIC_HOST)

response = es.delete_by_query(index="bus", body={"query": {"match_all": {}}}, ignore=[400, 404])
print("Resposta do Elasticsearch:", response)

response = es.delete_by_query(index="van", body={"query": {"match_all": {}}}, ignore=[400, 404])
print("Resposta do Elasticsearch:", response)

response = es.delete_by_query(index="stop", body={"query": {"match_all": {}}}, ignore=[400, 404])
print("Resposta do Elasticsearch:", response)

es.transport.close()

