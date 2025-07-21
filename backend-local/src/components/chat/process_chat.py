import json
from typing import cast
import uuid
from asyncio import Queue
from components.chat import ChatRequest, ChatResponse
from components.multi_kafka_response import Multi_Response
from resources.kafka import get_producer, chat_request_topic, get_consumer, chat_response_topic
from resources.kafka.rr_map import put_waiting_request

async def _send_to_kafka(query: str) -> Queue[Multi_Response]:
    producer = get_producer()
    if producer is None:
        raise Exception("Producer is not initialized")
    request_id = str(uuid.uuid4())
    chat_request = ChatRequest(
        request_id=request_id,
        query=query
    )
    queue: Queue[Multi_Response] = put_waiting_request(chat_response_topic, request_id)
    print(f"before send_and_wait")
    await producer.send_and_wait(chat_request_topic, chat_request.model_dump())
    print(f"after send_and_wait")
    return queue

async def process_chat(query: str):
    print(f"before _send_to_kafka")
    queue: Queue[Multi_Response] = await _send_to_kafka(query)
    print(f"after _send_to_kafka")
    while True:
        print(f"before queue.get")
        response = await queue.get()
        print(f"response: {response}")
        if response.is_last:            # the last response is the end of the chat and the content is empty
            # Send a final message to indicate the stream has ended
            data = {"message": "", "status": "completed"}
            yield f"data: {json.dumps(data)}\n\n"
            break
        print(f"after queue.get")
        chat_response = cast(ChatResponse, response)
        data = {"message": {"content": chat_response.response, "sender": chat_response.sender}}
        yield f"data: {json.dumps(data)}\n\n"
