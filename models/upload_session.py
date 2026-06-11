from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class UploadSession(SQLModel, table=True):
    __tablename__ = "UploadSession"
    session_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    user_id:UUID=Field(
        foreign_key="User.user_id"
    )
    title:str

    status:str ="pending"

    created_at: datetime=Field(
        default_factory=datetime.utcnow
    )
    completed_at: Optional[datetime]=None