from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from typing import Literal

class UploadSessionCreate(SQLModel):
    user_id:UUID
    title:str

class UploadSessionRead(SQLModel):
    user_id:UUID
    session_id: UUID
    title: str
    status:str
    created_at: datetime
    completed_at:Optional[datetime]=None

class UploadSessionUpdate(SQLModel):
    title:Optional[str]=None
    status:Optional[
        Literal[
            "pending",
            "processing",
            "completed",
            "failed"
        ]
    ]=None
    completed_at:Optional[datetime]=None