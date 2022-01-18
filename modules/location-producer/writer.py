import grpc
import location_pb2
import location_pb2_grpc
import os
import random
"""
Sample implementation of a writer that can be used to write messages to gRPC.
"""

print("Sending sample payload...")
LOCATION_GRPC_SERVER = 'localhost:5005'

channel = grpc.insecure_channel(LOCATION_GRPC_SERVER)
stub = location_pb2_grpc.LocationServiceStub(channel)
list1 = [1, 5, 6, 8, 9]
randomId = random.choice(list1)

# Update this with desired payload
item = location_pb2.LocationMessage(
    person_id=randomId,
    longitude=-122.290883,
    latitude=37.55363
)


response = stub.Create(item)