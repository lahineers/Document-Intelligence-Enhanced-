from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from sqlalchemy import Column
from typing import Dict,Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class SessionSummary(SQLModel, table=True):

    __tablename__="SessionSummary"
    session_summary_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    session_id:UUID=Field(
        foreign_key="UploadSession.session_id",
        index=True
    )
    summary_type: str
    content: str
    model_used: str
    doc_count:int
    combined_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    generated_at:datetime=Field(
        default_factory=datetime.utcnow
    )
