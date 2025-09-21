from kafka import KafkaProducer
from base import StorageEvent

class StorageEventProducer:
    def __init__(self, kafka_server='localhost:9092', topic='storage_events'):
        self.producer = KafkaProducer(bootstrap_servers=kafka_server)
        self.topic = topic

    def send_event(self, storage_event: StorageEvent):
        self.producer.send(self.topic, storage_event.to_json().encode('utf-8'))
        self.producer.flush()


