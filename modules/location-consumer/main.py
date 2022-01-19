from json.tool import main
from kafka import KafkaConsumer
from sqlalchemy.orm import declarative_base, sessionmaker
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Point
from sqlalchemy import BigInteger,Column,DateTime,Integer,create_engine,ForeignKey
from datetime import datetime
import os
import json
import logging

logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s, %(message)s', datefmt='%d/%b/%y, %H:%M:%S', level=logging.DEBUG)
TOPIC_NAME = os.environ['TOPIC_NAME']
KAFKA_SERVER = "% s:% s" % (os.environ['KAFKA_HOST_CONSUMER'], os.environ['KAFKA_PORT'])
DB_USER = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
Base=declarative_base()
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True)
Session=sessionmaker()
consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_SERVER, value_deserializer=lambda m: json.loads(m.decode('utf-8')))

class Location(Base):
    __tablename__='location'
    id = Column(BigInteger, primary_key=True)
    person_id = Column(Integer, nullable=False)
    coordinate = Column(Geometry("POINT"), nullable=False)
    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)

def persist_message(location):
    session=Session(bind=engine)
    location= Location(person_id=location["person_id"],coordinate=ST_Point(float(location["latitude"]), float(location["longitude"])))
    session.add(location)
    session.commit()

while True:
    for message in consumer:
        location = {'person_id':message[6]['person_id'], 'latitude': message[6]['latitude'], 'longitude': message[6]['longitude'] }
        persist_message(location)
        logging.debug(location)
        print(location)
        print (message.value)


