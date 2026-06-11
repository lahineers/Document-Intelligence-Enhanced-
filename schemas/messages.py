from uuid import UUID
from typing import Dict, Any,Optional
from sqlmodel import SQLModel
from datetime import datetime

class MessagesCreate(SQLModel):
    query_session_id: UUID
    role: str
    content:str
    tokens_used:int
    tools_calls:Dict[str,Any]

class MessagesRead(SQLModel):
    message_id:UUID
    query_session_id:UUID
    role:str
    content:str
    tool_calls:Dict[str,Any]
    source_chunks:Dict[str,Any]
    tokens_used: int
    created_at: datetime

class MessagesUpdate(SQLModel):
    content:Optional[str]=None
    token_used:Optional[int]=None
    tools_calls:Optional[
        Dict[str,Any]
    ]=None
    source_chunks:Optional[
        Dict[str,Any]
    ]=None
    