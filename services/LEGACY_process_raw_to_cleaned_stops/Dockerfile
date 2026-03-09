FROM python:3.9-slim

WORKDIR /app

# Install required dependencies
RUN apt-get update 
RUN pip install kafka-python

CMD ["python", "process.py"]
