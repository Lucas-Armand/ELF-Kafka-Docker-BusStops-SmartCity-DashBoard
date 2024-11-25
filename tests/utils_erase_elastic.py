from elasticsearch import Elasticsearch

# Configuração do Elasticsearch
ELASTIC_HOST = "http://elasticsearch:9200"

es = Elasticsearch(ELASTIC_HOST)

response = es.delete_by_query(index="_all", body={"query": {"match_all": {}}}, ignore=[400, 404])
print("Resposta do Elasticsearch:", response)

es.transport.close()

