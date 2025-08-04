import asyncio
import json
from typing import cast
import uuid
from asyncio import Queue
from components.chat import ChatRequest, ChatResponse
from resources.SysParam import sys_params
from components.multi_sqs_response import Multi_Response
import aioboto3
import os
from botocore.client import ClientError

from resources.sqs.rr_map import put_waiting_request

async def _send_to_sqs_message(query: str) -> list[Multi_Response] | None:
    print(f"Sending message to SQS: {sys_params['llm_chat_request_queue_url']}")
    async with aioboto3.Session().client("sqs", region_name=os.getenv("AWS_REGION")) as client:
        try:
            request_id = str(uuid.uuid4())
            chat_request = ChatRequest(request_id=request_id, query=query)
            message = {
                "QueueUrl": sys_params["llm_chat_request_queue_url"],
                "MessageBody": json.dumps(chat_request.model_dump())  # Convert to JSON string
            }
            task = asyncio.create_task(put_waiting_request(sys_params["llm_chat_response_queue_url"], request_id))
            print(f"before send_message")
            await client.send_message(**message)
            response_list = await task
            print(f"after send_message")
            return response_list
        except ClientError as e:
            print(f"Error sending to SQS: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

async def process_chat(query: str):
    print("before _send_to_kafka")
    response_list: list[Multi_Response] = await _send_to_sqs_message(query) or []
    print("after _send_to_kafka")
    while True:
        print("before list.pop")
        response = response_list.pop(0)
        print(f"response: {response}")
        if (
            response.is_last
        ):  # the last response is the end of the chat and the content is empty
            # Send a final message to indicate the stream has ended
            data = {"message": "", "status": "completed"}
            yield f"data: {json.dumps(data)}\n\n"
            break
        print("after list.pop")
        chat_response = cast(ChatResponse, response)
        data = {
            "message": {
                "content": chat_response.response,
                "sender": chat_response.sender,
            }
        }
        yield f"data: {json.dumps(data)}\n\n"
