from uuid import UUID
from sqlmodel import SQLModel

class ComparisonRequest(SQLModel):
    question: str
    document_ids: list[UUID]