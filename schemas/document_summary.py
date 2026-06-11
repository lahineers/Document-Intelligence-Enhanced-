from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel


class DocumentSummaryCreate(SQLModel):
    doc_id: UUID
    content: str
    model_used: str


class DocumentSummaryRead(SQLModel):
    document_summary_id: UUID
    document_id: UUID
    summary_type:str
    content: str
    model_used: str
    key_metrics:Dict[str,Any]
    generated_at: Optional[datetime] = None
