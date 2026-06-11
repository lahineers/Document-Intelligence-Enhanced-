from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from sqlalchemy import Column
from typing import Dict,Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
class DocumentChunk(SQLModel, table=True):

    __tablename__="DocumentChunk"
    chunk_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    doc_id:UUID=Field(
        foreign_key="Document.doc_id"
    )
    chunk_text: str
    chunk_index: int
    page_number: int
    heading: str
    embedding_status: str="pending"
    token_count:int=0
    section_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )

    created_at:datetime=Field(
        default_factory=datetime.utcnow
    )
