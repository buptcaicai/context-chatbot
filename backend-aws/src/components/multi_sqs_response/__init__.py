from pydantic import BaseModel

class Multi_Response(BaseModel):
    request_id: str
    sort_id: int
    is_last: bool = True
