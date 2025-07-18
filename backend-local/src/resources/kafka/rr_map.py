from asyncio import Future
from kafka import future

from components.file_upload import FileContentResponse


__rr_map = {}

def init_rr_map(request_topic: str):
    __rr_map[request_topic] = {}

def put_waiting_request(request_topic: str, request_id: str):
    if request_topic not in __rr_map:
        init_rr_map(request_topic)
    future = Future()
    __rr_map[request_topic][request_id] = future
    return future

def match_request(request_topic: str, response: FileContentResponse):
    future = __rr_map[request_topic].get(response.request_id)
    if future is None:
        return
    future.set_result(response)
    del __rr_map[request_topic][response.request_id]
