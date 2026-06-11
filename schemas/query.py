from uuid import UUID
from datetime import datetime

from sqlmodel import SQLModel


class QueryRequest(SQLModel):

    query: str
    document_id:UUID

class QueryCreate(SQLModel):

    question: str

    answer: str


class QueryRead(SQLModel):

    query_id: UUID

    question: str

    answer: str

    created_at: datetime