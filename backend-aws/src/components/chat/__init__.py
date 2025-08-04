from typing import Literal
from pydantic import BaseModel
from ..multi_sqs_response import Multi_Response

class ChatRequest(BaseModel):
    request_id: str
    query: str

class ChatResponse(Multi_Response):
    sender: Literal["ai", "user"]
    response: str
