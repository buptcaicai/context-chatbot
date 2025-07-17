import os
import json
from kafka import KafkaProducer

__producer: KafkaProducer | None = None

def create_producer():
    global __producer
    __producer = KafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BROKER")],
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        batch_size=1000000,
        linger_ms=500,
    )

def get_producer():
    global __producer
    return __producer
