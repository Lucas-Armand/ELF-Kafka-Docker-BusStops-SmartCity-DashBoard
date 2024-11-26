from elasticsearch import Elasticsearch

ELASTIC_HOST = "http://elasticsearch:9200"
INDEX_NAME = "test-index"
DOC_ID = "1"
DOC_BODY = {"message": "Test Elasticsearch integration"}

es = Elasticsearch(ELASTIC_HOST)

# Create an index
es.indices.create(index=INDEX_NAME, ignore=400)
print(f"Index '{INDEX_NAME}' created.")

# Index a document
es.index(index=INDEX_NAME, id=DOC_ID, document=DOC_BODY)
print(f"Document {DOC_ID} indexed.")

# Check if the document has been saved
response = es.get(index=INDEX_NAME, id=DOC_ID)
if response["_source"] == DOC_BODY:
    print(f"Document {DOC_ID} retrieved successfully.")
else:
    print(f"Failed to retrieve document {DOC_ID}.")

es.transport.close()

