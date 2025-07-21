from pydantic import BaseModel
from typing import List, Literal
from components.multi_kafka_response import Multi_Response

class FileContentRequest(BaseModel):       # TODO: use file name and size to identify the file is not good enough
    request_id: str
    file_name: str
    file_size: int
    sentences: List[str]
    is_last: bool

    def __init__(self, request_id: str, file_name: str, file_size: int, sentences: List[str], is_last: bool):
        super().__init__(request_id=request_id, file_name=file_name, file_size=file_size, sentences=sentences, is_last=is_last)
class FileContentResponse(Multi_Response):
    file_name: str
    status: Literal["success", "error"]
    error_message: str | None = None