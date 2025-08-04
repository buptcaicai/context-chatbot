import dotenv
dotenv.load_dotenv(override=True)
import os
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

config = {"configurable": {"thread_id": "dddww"}}

input_message = (
    "Tell me about Australia\n\n"
    "Once you get the answer, tell me about the capital city."
)
agent_executor = create_react_agent(llm, [retrieve])  # type: ignore

for event in agent_executor.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
    config=config,  # type: ignore
):
    print("type: ", event["messages"][-1].type)
    event["messages"][-1].pretty_print()
