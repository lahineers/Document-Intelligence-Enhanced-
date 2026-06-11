from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel


class SessionSummaryCreate(SQLModel):
    session_id: UUID
    content: str
    model_used: str
    doc_count: int


class SessionSummaryRead(SQLModel):
    session_summary_id: UUID
    session_id: UUID
    summary_type:str
    content: str
    model_used: str
    combined_metrics:Dict[str,Any]
    doc_count:int
    generated_at: Optional[datetime] = None
