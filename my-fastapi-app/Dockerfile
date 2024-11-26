FROM python:3.9-slim

WORKDIR /app

# Instale as dependências necessárias
RUN apt-get update 
RUN pip install datetime
RUN pip install kafka-python
RUN pip install fastapi
RUN pip install uvicorn

CMD ["uvicorn", "producer:app", "--host", "0.0.0.0", "--port", "8000"]
