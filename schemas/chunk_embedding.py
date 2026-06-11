from uuid import UUID
from datetime import datetime

from sqlmodel import SQLModel


class ChunkEmbeddingCreate(SQLModel):
    chunk_id:UUID
    embedding: list[float]
    model_name:str
    

class ChunkEmbeddingRead(SQLModel):
    embedding_id:UUID
    chunk_id:UUID
    embedding:list[float]
    model_name:str
    created_at:datetime

