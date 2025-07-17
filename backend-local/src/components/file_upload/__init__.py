from pydantic import BaseModel
from typing import List

class FileContent(BaseModel):       # TODO: use file name and size to identify the file is not good enough
    file_name: str
    file_size: int
    sentences: List[str]
    is_last: bool
