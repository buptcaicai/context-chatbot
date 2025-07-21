import traceback
import dotenv
import redis
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import uuid
dotenv.load_dotenv(override=True)
import os
from kafka import KafkaConsumer, KafkaProducer
import json
from components.file_upload import FileContentRequest, FileContentResponse
from resources.kafka import file_ingest_request_topic, file_ingest_response_topic

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

consumer = KafkaConsumer(
    file_ingest_request_topic,
    bootstrap_servers=[os.getenv("KAFKA_BROKER")],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
)

producer = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_BROKER")],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
# tp = TopicPartition("file-ingest", 0)
# consumer.assign([tp])
# consumer.seek(tp, 5)
for message in consumer:
    try:
        print(f"Received message offset: {message.offset}")
        print(f"Received message: {message}")
        data = message.value

        file_content_request = FileContentRequest(
            request_id=data.get("request_id"),
            file_name=data.get("file_name"),
            file_size=data.get("file_size"),
            sentences=data.get("sentences", []),
            is_last=data.get("is_last", False)
        )

        print(f"Created FileContent object for file: {file_content_request.file_name}")
        print(f"File size: {file_content_request.file_size}")
        print(f"Number of sentences: {len(file_content_request.sentences)}")
        print(f"Is last chunk: {file_content_request.is_last}")

        for text in file_content_request.sentences:
            embedding = model.encode(text).tolist()
            qdrant_client.upsert(
                collection_name=qdrant_collection,
                points=[models.PointStruct(id=str(uuid.uuid4()), vector=embedding, payload={"text": text})],
                wait=True
            )

        if file_content_request.is_last:
            response = FileContentResponse(
                request_id=file_content_request.request_id,
                status="success",
                file_name=file_content_request.file_name,
            )
            producer.send(file_ingest_response_topic, response.model_dump())
            print(f"Sent response to {file_ingest_response_topic}: {response.model_dump()}")
            if redis_client is not None:
                redis_client.zadd("file-ingested-zset", {f"{file_content_request.file_name}::{file_content_request.file_size}": 0})
            else:
                print("Redis client is not initialized")
    except Exception as e:
        print(f"Error processing message: {e}")
        stack_trace = traceback.format_exc()
        print(f"Stack trace:\n{stack_trace}")
        
    