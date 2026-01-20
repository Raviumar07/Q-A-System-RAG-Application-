from pydantic import BaseModel
from typing import List, Optional

class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[dict]] = []