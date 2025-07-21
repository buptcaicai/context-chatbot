import asyncio
import os
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from components.chat import ChatResponse
from resources.kafka.rr_map import match_request
from components.file_upload import FileContentResponse

__consumer_running: bool = False
__producer = None
__consumer = None
__consumer_task = None
file_ingest_request_topic = "file-ingest-request"
file_ingest_response_topic = "file-ingest-response"
chat_request_topic = "chat-request"
chat_response_topic = "chat-response"

def get_producer():
    global __producer
    return __producer

def get_consumer():
    global __consumer
    return __consumer

async def init_kafka():
    global __consumer_task
    await _create_producer()
    await _create_consumer()
    print(f"before _run_consumer")
    # Run consumer as background task instead of blocking
    __consumer_task = asyncio.create_task(_run_consumer())
    print(f"after _run_consumer")

async def shutdown_kafka():
    await _shutdown_producer()
    await _shutdown_consumer()

async def _create_producer():
    global __producer
    __producer = AIOKafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BROKER")],
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        max_batch_size=1000000,
        linger_ms=500,
    )
    await __producer.start()

async def _create_consumer():
    global __consumer
    __consumer = AIOKafkaConsumer(
        bootstrap_servers=[os.getenv("KAFKA_BROKER")],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    __consumer.subscribe([file_ingest_response_topic, chat_response_topic])
    await __consumer.start()

async def _run_consumer():
    global __consumer, __consumer_running
    __consumer_running = True
    try:
        while __consumer_running:
            async for message in __consumer:
                response = None
                if message.topic == file_ingest_response_topic:
                    response = FileContentResponse(
                        request_id=message.value.get("request_id"),
                        status=message.value.get("status"),
                        file_name=message.value.get("file_name"),
                        error_message=message.value.get("error_message")
                    )
                elif message.topic == chat_response_topic:
                    response = ChatResponse(
                        sender=message.value.get("sender"),
                        request_id=message.value.get("request_id"),
                        response=message.value.get("response"),
                        is_last=message.value.get("is_last")
                    )
                if response is not None:
                    await match_request(message.topic, response)
    except Exception as e:
        print(f"Consumer error: {e}")
    finally:
        __consumer_running = False

async def _shutdown_consumer():
    global __consumer, __consumer_running, __consumer_task
    __consumer_running = False
    if __consumer_task:
        __consumer_task.cancel()
        try:
            await __consumer_task
        except asyncio.CancelledError:
            pass
    await __consumer.stop()

async def _shutdown_producer():
    global __producer
    await __producer.flush()
    await __producer.stop()
