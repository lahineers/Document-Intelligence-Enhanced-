from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from typing import Literal

from sqlmodel import SQLModel


class DocumentCreate(SQLModel):
    user_id: UUID
    session_id: UUID

    doc_type: str
    #file_name: str
    #file_type: str

    #doc_path: str


class DocumentRead(SQLModel):
    doc_id: UUID

    user_id: UUID
    session_id: UUID

    doc_type: str
    file_name: str
    file_type: str

    markdown_object_key: str | None = None

    doc_path: str

    page_count: int
    file_size_bytes: int

    upload_time: datetime

    extracted_metadata: Dict[str, Any]

    processing_status: str

    processed_at: Optional[datetime] = None


class DocumentUpdate(SQLModel):
    processing_status: Optional[
        Literal[
            "pending",
            "processing",
            "chunking",
            "summarizing"
            "completed",
            "failed"
        ]
    ] = None

    page_count: Optional[int] = None

    file_size_bytes: Optional[int] = None

    extracted_metadata: Optional[
        Dict[str, Any]
    ] = None

    processed_at: Optional[datetime] = None