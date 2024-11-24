from elasticsearch import Elasticsearch

ELASTIC_HOST = "http://elasticsearch:9200"
INDEX_NAME = "test-index"
DOC_ID = "1"
DOC_BODY = {"message": "Test Elasticsearch integration"}

es = Elasticsearch(ELASTIC_HOST)

# Cria um índice
es.indices.create(index=INDEX_NAME, ignore=400)
print(f"Index '{INDEX_NAME}' created.")

# Indexa um documento
es.index(index=INDEX_NAME, id=DOC_ID, document=DOC_BODY)
print(f"Document {DOC_ID} indexed.")

# Verifica se o documento foi salvo
response = es.get(index=INDEX_NAME, id=DOC_ID)
if response["_source"] == DOC_BODY:
    print(f"Document {DOC_ID} retrieved successfully.")
else:
    print(f"Failed to retrieve document {DOC_ID}.")

if __name__ == "__main__":
    test_elastic()

