FROM python:3.9-slim

WORKDIR /app/tests

RUN apt-get update 
RUN apt-get install -y curl
RUN pip install kafka-python
RUN pip install elasticsearch
RUN pip install requests
RUN pip install protobuf
RUN pip install gtfs-realtime-bindings
RUN pip install pandas  
RUN pip install numpy

CMD ["bash"]

