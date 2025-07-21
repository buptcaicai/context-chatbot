from pydantic import BaseModel

class Multi_Response(BaseModel):
    request_id: str
    is_last: bool = True
