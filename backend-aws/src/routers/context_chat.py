from fastapi import APIRouter, Body, Query
from starlette.responses import StreamingResponse

from components.chat.process_chat import process_chat

router = APIRouter()

@router.get("/start")
async def start_chat(query: str = Query(...)):
    print(f"query: {query}")
    return StreamingResponse(process_chat(query), media_type="text/event-stream")
