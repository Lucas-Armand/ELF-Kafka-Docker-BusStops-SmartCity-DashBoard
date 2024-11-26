FROM python:3.9-slim

WORKDIR /app

# Instale as dependências necessárias
RUN apt-get update 
RUN pip install kafka-python

CMD ["python", "process.py"]
