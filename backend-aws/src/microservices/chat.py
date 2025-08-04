import asyncio
import uuid
import aioboto3
from botocore.client import ClientError
import dotenv
from ..components.chat import ChatRequest, ChatResponse
from ..resources.SysParam import get_ssm_parameters_async, sys_params
dotenv.load_dotenv(override=True)
import os
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

async def process_chat_request():
    global agent_executor
    await get_ssm_parameters_async()
    async with aioboto3.Session().client("sqs", region_name=os.getenv("AWS_REGION")) as client:
        try:
            while True:
                response = await client.receive_message(
                    QueueUrl=sys_params["llm_chat_request_queue_url"],
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                    MessageAttributeNames=["All"],
                ) 
                messages = response.get("Messages", [])
                if not messages:
                    print(
                        f"No messages received from llm chat request queue, continuing to poll..."
                    )
                    continue
                for message in messages:
                    body = json.loads(message.get("Body", "{}"))
                    message_id = message.get("MessageId")
                    receipt_handle = message.get("ReceiptHandle")
                    chat_request = ChatRequest(**body)
                    print(f"Received message from llm chat request queue, ID: {message_id}")
                    await client.delete_message(
                        QueueUrl=sys_params["llm_chat_request_queue_url"],
                        ReceiptHandle=receipt_handle,
                    )

                    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
                    sort_id = 0
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
                                sort_id=(sort_id:=sort_id+1),
                                is_last=False,
                            )
                            print(f"sending chat_response")
                            await client.send_message(
                                QueueUrl=sys_params["llm_chat_response_queue_url"],
                                MessageBody=json.dumps(chat_response.model_dump()),
                            )
                    print(f"before end_of_response")
                    end_of_response = ChatResponse(
                        request_id=chat_request.request_id,
                        sender="ai",
                        response="",
                        sort_id=(sort_id:=sort_id+1),
                        is_last=True,
                    )
                    await client.send_message(
                        QueueUrl=sys_params["llm_chat_response_queue_url"],
                        MessageBody=json.dumps(end_of_response.model_dump()),
                    )

        except ClientError as e:
            print(f"Error reading from llm chat request queue: {e}")
        except KeyboardInterrupt:
            print(f"Stopping llm chat request queue reader...")
        except Exception as e:
            print(f"Unexpected error in llm chat request queue: {e}")


asyncio.run(process_chat_request())
