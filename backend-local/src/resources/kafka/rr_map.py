from asyncio import Queue

from components.multi_kafka_response import Multi_Response

__rr_map = {}

def init_rr_map(response_topic: str):
    __rr_map[response_topic] = {}

def put_waiting_request(response_topic: str, request_id: str):
    if response_topic not in __rr_map:
        init_rr_map(response_topic)
    queue: Queue[Multi_Response] = Queue()    # use queue to allow multiple messages to be sent to the same request_id
    __rr_map[response_topic][request_id] = queue
    return queue


async def match_request(response_topic: str, response: Multi_Response):
    queue: Queue[Multi_Response] | None = __rr_map[response_topic].get(response.request_id)
    if queue is None:
        return
    await queue.put(response)
    if response.is_last:
        del __rr_map[response_topic][response.request_id]
