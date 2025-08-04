import asyncio
from botocore.client import ClientError
import dotenv
import redis
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import uuid
dotenv.load_dotenv(override=True)
import os
import json
import aioboto3
from ..components.file_upload import FileContentRequest
from ..resources.SysParam import sys_params, get_ssm_parameters_async

redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True) # type: ignore
qdrant_client = QdrantClient(host=os.getenv("QDRANT_HOST"), port=int(os.getenv("QDRANT_PORT") or "6333"))
qdrant_collection = os.getenv("QDRANT_COLLECTION") or "ingested_docs"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vector_size = 384   # embedding size from all-MiniLM-L6-v2

if not qdrant_client.collection_exists(qdrant_collection):
    qdrant_client.create_collection(
        collection_name=qdrant_collection,
        vectors_config=models.VectorParams(
            size=vector_size, distance=models.Distance.COSINE
        ),
    )

async def read_sqs_messages():
    await get_ssm_parameters_async()
    async with aioboto3.Session().client("sqs", region_name=os.getenv("AWS_REGION")) as client:
        try:
            while True:
                response = await client.receive_message(
                    QueueUrl=sys_params["file_ingestion_request_queue_url"],
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                    MessageAttributeNames=["All"],
                )
                # Process messages if any
                messages = response.get("Messages", [])
                if not messages:
                    print(
                        f"No messages received from file ingestion request queue, continuing to poll..."
                    )
                    continue

                for message in messages:
                    # Parse message body
                    body = json.loads(message.get("Body", "{}"))
                    message_id = message.get("MessageId")
                    receipt_handle = message.get("ReceiptHandle")

                    file_content_request = FileContentRequest(
                        request_id=body.get("request_id"),
                        file_name=body.get("file_name"),
                        file_size=body.get("file_size"),
                        sentences=body.get("sentences", []),
                        is_last=body.get("is_last", False)
                    )

                    for text in file_content_request.sentences:
                        embedding = model.encode(text).tolist()
                        qdrant_client.upsert(
                            collection_name=qdrant_collection,
                            points=[models.PointStruct(id=str(uuid.uuid4()), vector=embedding, payload={"text": text})],
                            wait=True
                        )

                    print(f"Received message from file ingestion request queue, ID: {message_id}")
                    print(f"Message body: {body}")

                    # Delete message after processing
                    await client.delete_message(
                        QueueUrl=sys_params["file_ingestion_request_queue_url"], ReceiptHandle=receipt_handle
                    )
                    print(f"Deleted message from file ingestion request queue, ID: {message_id}")

                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
        except ClientError as e:
            print(f"Error reading from file ingestion request queue: {e}")
        except KeyboardInterrupt:
            print(f"Stopping file ingestion request queue reader...")
        except Exception as e:
            print(f"Unexpected error in file ingestion request queue: {e}")

asyncio.run(read_sqs_messages())
