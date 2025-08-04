import asyncio
from components.multi_sqs_response import Multi_Response

__rr_map = {}

def init_rr_map(response_url: str):
    __rr_map[response_url] = {}

async def put_waiting_request(response_url: str, request_id: str):
    if response_url not in __rr_map:
        init_rr_map(response_url)
    response_list: list[Multi_Response] = []     # use list to allow multiple messages to be sent to the same request_id
    __rr_map[response_url][request_id] = response_list
    while True:
        await asyncio.sleep(0.5)
        if response_list and response_list[-1].is_last:
            response_list.sort(key=lambda x: x.sort_id)
            break
    print(f"response_list: {response_list}")
    return response_list

def match_request(response_url: str, response: Multi_Response):
    response_list: list[Multi_Response] | None = __rr_map[response_url].get(response.request_id)
    if response_list is None:
        return
    print(f"match_ request response: {response}")
    response_list.append(response)
    if response.is_last:
        del __rr_map[response_url][response.request_id]
