from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel,Field


class QuerySessionCreate(SQLModel):
    upload_session_id:UUID
    title:str

class QuerySessionRead(SQLModel):
    query_session_id: UUID
    user_id: UUID
    upload_session_id: UUID
    title:str
    created_at:datetime
    updated_at:Optional[datetime]=None

class QuerySessionUpdate(SQLModel):
    updated_at:Optional[datetime]=None