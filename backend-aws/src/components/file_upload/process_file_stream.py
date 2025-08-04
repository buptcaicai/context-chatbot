from asyncio import Queue
import json
import os
import aioboto3
from botocore.client import ClientError
import nltk
import logging
import uuid
from resources.SysParam import sys_params
from . import FileContentRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_SENTENCE_LENGTH = 512
MAX_MESSAGE_SIZE = 100_000  # 100k
CHUNK_SIZE = 50_000  # 50KB chunks


async def _send_sqs_message(file_name: str, file_size: int, sentences, is_last: bool):
    # Create an async session
    print(f"Sending message to SQS: {sys_params['file_ingestion_request_queue_url']}")
    async with aioboto3.Session().client("sqs", region_name=os.getenv("AWS_REGION")) as client:
        try:
            request_id = str(uuid.uuid4())
            file_content = FileContentRequest(request_id=request_id, file_name=file_name, file_size=file_size, sentences=sentences, is_last=is_last)
            message = {
                "QueueUrl": sys_params["file_ingestion_request_queue_url"],
                "MessageBody": json.dumps(file_content.model_dump()),  # Convert to JSON string
            }

            await client.send_message(**message)

        except ClientError as e:
            print(f"Error sending to SQS: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

async def process_stream(input_stream, file_name: str, file_size: int):
    """Process text stream chunk by chunk, tokenizing sentences."""
    tokenizer = nltk.tokenize.PunktSentenceTokenizer()
    buffer = ""
    sentences_cache = []
    buffer_size = 0
    try:
        while True:
            chunk = input_stream.read(CHUNK_SIZE)
            if not chunk:
                if buffer:
                    sentences = tokenizer.tokenize(buffer)
                    sentences_cache.extend(sentences)
                    await _send_sqs_message(file_name, file_size, sentences_cache, is_last=True)
                    sentences_cache = []
                break

            # Decode chunk (assume UTF-8) and add to buffer
            buffer += chunk.decode("utf-8", errors="ignore")
            buffer_size += len(buffer)
            # Tokenize sentences, keeping incomplete ones in buffer
            sentences = tokenizer.tokenize(buffer)
            if sentences:
                sentences_cache.extend(sentences)
                if buffer_size > MAX_MESSAGE_SIZE:
                    await _send_sqs_message(file_name, file_size, sentences_cache, is_last=False)
                    sentences_cache = []
                    buffer_size = 0
                buffer = sentences[-1]  # Keep last (potentially incomplete) sentence

    except Exception as e:
        logger.error(f"Error processing stream: {str(e)}")
        raise
