from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel


class DocumentSummaryCreate(SQLModel):
    doc_id: UUID
    content: str
    model_used: str
    key_metrics: Dict[str, Any] = {}


class DocumentSummaryRead(SQLModel):
    summary_id: UUID
    doc_id: UUID

    content: str
    model_used: str

    key_metrics: Dict[str, Any]

    generated_at: Optional[datetime] = None