from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
from datetime import datetime

class ChunkEmbedding(SQLModel, table=True):

    __tablename__="ChunkEmbedding"
    embedding_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    chunk_id:UUID=Field(
        foreign_key="DocumentChunk.chunk_id",
        index=True
    )

    model_name:str

    embedding: list[float]=Field(
        sa_column=Column(Vector(4096))
    )

    created_at:datetime=Field(
        default_factory=datetime.utcnow
    )
