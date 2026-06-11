from uuid import uuid4, UUID
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class QuerySession(SQLModel, table=True):
    __tablename__="QuerySession"
    query_session_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    user_id: UUID=Field(
        foreign_key="User.user_id",
        index=True
    )
    upload_session_id: UUID=Field(
        foreign_key="UploadSession.session_id",
        index=True
    )
    title:str
    created_at: datetime=Field(
        default_factory=datetime.utcnow
    )
    updated_at:Optional[datetime]=None