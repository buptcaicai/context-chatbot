from pydantic import BaseModel
from typing import List

class FileContentRequest(BaseModel):       # TODO: use file name and size to identify the file is not good enough
    request_id: str
    file_name: str
    file_size: int
    sentences: List[str]
    is_last: bool

    def __init__(self, request_id: str, file_name: str, file_size: int, sentences: List[str], is_last: bool):
        super().__init__(request_id=request_id, file_name=file_name, file_size=file_size, sentences=sentences, is_last=is_last)