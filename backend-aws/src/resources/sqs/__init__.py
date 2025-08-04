import asyncio
import os
import json
import aioboto3
from botocore.client import ClientError
from components.chat import ChatResponse
from resources.SysParam import sys_params
from resources.sqs.rr_map import match_request


_running = False
async def start_sqs_consumers():
    print(f"Starting llm chat response queue consumer")
    global _running
    _running = True
    async with aioboto3.Session().client("sqs", region_name=os.getenv("AWS_REGION")) as client: # type: ignore
        try:
            while _running:
                response = await client.receive_message(
                    QueueUrl=sys_params["llm_chat_response_queue_url"],
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                    MessageAttributeNames=["All"],
                )

                # Process messages if any
                messages = response.get("Messages", [])
                if not messages:
                    print(
                        f"No messages received from llm chat response queue, continuing to poll..."
                    )
                    continue

                for message in messages:
                    # Parse message body
                    body = json.loads(message.get("Body", "{}"))
                    message_id = message.get("MessageId")
                    receipt_handle = message.get("ReceiptHandle")

                    chat_response = ChatResponse(
                        request_id=body.get("request_id"),
                        response=body.get("response"),
                        is_last=body.get("is_last", False),
                        sort_id=body.get("sort_id", 0),
                        sender=body.get("sender", "ai"),
                    )

                    match_request(sys_params["llm_chat_response_queue_url"], chat_response)
                    print(f"Received message from llm chat request queue, ID: {message_id}")
                    print(f"Message body: {body}")

                    # Delete message after processing
                    await client.delete_message(
                        QueueUrl=sys_params["llm_chat_response_queue_url"], ReceiptHandle=receipt_handle
                    )
                    print(f"Deleted message from llm chat response queue, ID: {message_id}")

                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
        except ClientError as e:
            print(f"Error reading from llm chat response queue: {e}")
        except KeyboardInterrupt:
            print(f"Stopping llm chat response queue reader...")
        except Exception as e:
            print(f"Unexpected 123 error in llm chat response queue: {e}")

async def stop_sqs_consumers():
    global _running
    _running = False
