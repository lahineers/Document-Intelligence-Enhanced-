from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from typing import Literal

from sqlmodel import SQLModel,Field


class DocumentChunkCreate(SQLModel):
    doc_id:UUID
    heading: str | None = Field(
        default=None,
        max_length=255
    )
    chunk_text:str
    chunk_index: int
    page_number: int

class DocumentChunkRead(SQLModel):
    doc_id: UUID
    chunk_id: UUID
    chunk_text: str
    chunk_index:int
    page_number: int
    token_count:int
    heading:Optional[str]
    embedding_status:str
    section_metadata:Dict[str, Any]
    created_at:datetime

