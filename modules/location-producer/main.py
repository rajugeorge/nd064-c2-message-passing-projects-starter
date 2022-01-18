import time
from concurrent import futures
from kafka import KafkaProducer

import grpc
import location_pb2
import location_pb2_grpc
import json
import os
import logging

logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s, %(message)s', datefmt='%d/%b/%y, %H:%M:%S', level=logging.DEBUG)

class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):

        TOPIC_NAME = os.environ['TOPIC_NAME']
        KAFKA_SERVER = "% s:% s" % (os.environ['KAFKA_HOST_PRODUCER'], os.environ['KAFKA_PORT'])

        request_value = {
            "person_id": int(request.person_id),
            "longitude": request.longitude,
            "latitude": request.latitude
        }
        print(request_value)
        logging.debug(request_value)

        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        pl = json.dumps(request_value)
        producer.send(TOPIC_NAME, request_value)
        producer.flush()

        return location_pb2.LocationMessage(**request_value)


# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

print("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)