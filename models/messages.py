from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel,Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from typing import Dict,Any

class Messages(SQLModel, table=True):
    __tablename__="Messages"
    message_id: UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    query_session_id: UUID=Field(
        foreign_key="QuerySession.query_session_id",
        index=True
    )
    role:str
    content:str
    tool_calls:Dict[str,Any]=Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    source_chunks:Dict[str,Any]=Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    tokens_used:int
    created_at:datetime=Field(
        default_factory=datetime.utcnow
    )