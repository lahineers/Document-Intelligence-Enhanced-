from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any,Dict
from sqlalchemy import Column
from uuid import UUID, uuid4

class DocumentSummary(SQLModel, table=True):
    __tablename__="DocumentSummary"
    summary_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    doc_id:UUID=Field(
        foreign_key="Document.doc_id",
        index=True
    )

    content:str
    model_used:str
    key_metrics:Dict[str,Any]=Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    generated_at:datetime=Field(
        default_factory=datetime.utcnow
    )