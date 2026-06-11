from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import SQLModel, Field


class Query(SQLModel, table=True):

    __tablename__ = "Query"

    query_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True
    )

    question: str

    answer: str

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )