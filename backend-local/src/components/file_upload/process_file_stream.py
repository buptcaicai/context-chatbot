import nltk
import logging
import uuid
from resources.kafka import get_producer
from resources.kafka.rr_map import put_waiting_request
from . import FileContentRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_SENTENCE_LENGTH = 512
MAX_MESSAGE_SIZE = 100_000  # 100k
CHUNK_SIZE = 50_000  # 50KB chunks

def send_to_kafka(file_name: str, file_size: int, sentences, is_last: bool, topic="file-injest"):
    producer = get_producer()
    if producer is None:
        raise Exception("Producer is not initialized")
    request_id = str(uuid.uuid4())
    file_content = FileContentRequest(request_id=request_id, file_name=file_name, file_size=file_size, sentences=sentences, is_last=is_last)
    print(f"before sending to kafka")
    future = None
    if is_last:
        future = put_waiting_request(topic, request_id)
    producer.send(topic, file_content.model_dump())
    print("sent to kafka")
    return future

def process_stream(input_stream, file_name: str, file_size: int):
    """Process text stream chunk by chunk, tokenizing sentences."""
    tokenizer = nltk.tokenize.PunktSentenceTokenizer()
    buffer = ""
    sentences_cache = []
    buffer_size = 0
    future = None
    try:
        while True:
            chunk = input_stream.read(CHUNK_SIZE)
            if not chunk:
                # Process remaining buffer
                if buffer:
                    sentences = tokenizer.tokenize(buffer)
                    sentences_cache.extend(sentences)
                    future = send_to_kafka(file_name, file_size, sentences_cache, is_last=True)
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
                    send_to_kafka(file_name, file_size, sentences_cache, is_last=False)
                    sentences_cache = []
                    buffer_size = 0
                buffer = sentences[-1]  # Keep last (potentially incomplete) sentence

    except Exception as e:
        logger.error(f"Error processing stream: {str(e)}")
        raise
    
    return future
