import uuid
import dotenv

from components.chat import ChatRequest, ChatResponse
from resources.kafka import chat_request_topic, chat_response_topic
dotenv.load_dotenv(override=True)
import os
from kafka import KafkaConsumer, KafkaProducer
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
qdrant_client = QdrantClient(host=os.getenv("QDRANT_HOST"), port=int(os.getenv("QDRANT_PORT") or "6333"))
qdrant_collection = os.getenv("QDRANT_COLLECTION") or "ingested_docs"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

consumer = KafkaConsumer(
    chat_request_topic,
    bootstrap_servers=[os.getenv("KAFKA_BROKER")],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
)

producer = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_BROKER")],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

@tool(response_format="content")
def retrieve(query: str):
    """Retrieve information related to a query."""
    print(f"Retrieving for query: {query}")
    results = qdrant_client.query_points(
        collection_name=qdrant_collection,
        query=model.encode(query).tolist(),
        limit=10,
    ).points
    retrieved_docs = [result.payload["text"] for result in results]  # type: ignore
    serialized = "\n\n".join(retrieved_docs)
    print(f"serialized: {serialized}")
    print(f"retrieved_docs: {retrieved_docs}")  # Debugging output
    print(f"Number of retrieved documents: {len(retrieved_docs)}")  # Debugging output
    return serialized

agent_executor = create_react_agent(llm, [retrieve])
for message in consumer:
    try:
        print(f"Received message offset: {message.offset}")
        print(f"Received message: {message}")
        data = message.value
        chat_request = ChatRequest(**data)
        print(f"Chat request: {chat_request}")

        # get top 10 results from qdrant
        results = qdrant_client.query_points(
            collection_name=qdrant_collection,
            query=model.encode(chat_request.query).tolist(),
            limit=10,
            with_payload=True,
        )

        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        for event in agent_executor.stream(
            {"messages": [{"role": "user", "content": chat_request.query}]},
            stream_mode="values",
            config=config,  # type: ignore
        ):
            event["messages"][-1].pretty_print()
            print(f"message type: {event['messages'][-1].type}")
            if event["messages"][-1].type == "ai" or event["messages"][-1].type == "human":
                chat_response = ChatResponse(
                    request_id=chat_request.request_id,
                    sender=event["messages"][-1].type == "ai" and "ai" or "user",
                    response=event["messages"][-1].content,
                    is_last=False,
                )
                print(f"sending chat_response")
                producer.send(chat_response_topic, chat_response.model_dump())
        print(f"before end_of_response")
        end_of_response = ChatResponse(
            request_id=chat_request.request_id,
            sender="ai",
            response="",
            is_last=True,
        )
        producer.send(chat_response_topic, end_of_response.model_dump())
    except Exception as e:
        print(f"Error: {e}")
