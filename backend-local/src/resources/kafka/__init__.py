import asyncio
import os
import json
from kafka import KafkaConsumer, KafkaProducer
from resources.kafka.rr_map import match_request
from components.file_upload import FileContentResponse

__producer: KafkaProducer | None = None
__consumer: KafkaConsumer | None = None
__consumer_running: bool = False
request_topic = "file-injest"
response_topic = "file-injest-response"

def create_producer():
    global __producer
    __producer = KafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BROKER")],
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        batch_size=1000000,
        linger_ms=500,
    )

def create_consumer():
    global __consumer
    __consumer = KafkaConsumer(
        response_topic,
        bootstrap_servers=[os.getenv("KAFKA_BROKER")],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

def get_producer():
    global __producer
    return __producer

def get_consumer():
    global __consumer
    return __consumer

def run_consumer(request_topic: str):
    global __consumer, __consumer_running
    if __consumer is None:
        raise Exception("Consumer is not initialized")
    __consumer_running = True
    while __consumer_running:
        records = __consumer.poll(timeout_ms=1000)
        for topic_partition, messages in records.items():
            for message in messages:
                print(message)
                response = FileContentResponse(
                    request_id=message.value.get("request_id"),
                    status=message.value.get("status"),
                    file_name=message.value.get("file_name"),
                    error_message=message.value.get("error_message")
                )
                match_request(request_topic, response)
    return None

def run_consumer_async(request_topic: str):
    global __consumer
    if __consumer is None:
        raise Exception("Consumer is not initialized")
    return asyncio.create_task(asyncio.to_thread(run_consumer, request_topic))

def shutdown_consumer():
    global __consumer, __consumer_running
    __consumer_running = False
    if __consumer is not None:
        __consumer.close()
