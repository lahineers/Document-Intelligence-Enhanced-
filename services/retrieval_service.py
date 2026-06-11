from sqlmodel import Session, select
from uuid import UUID
from models.document_chunk import DocumentChunk
from models.chunk_embedding import ChunkEmbedding

from services.embedding_service import (
    EmbeddingService
)


class RetrievalService:

    @staticmethod
    def retrieve_chunks(
        query: str,
        document_id:UUID,
        session: Session,
        top_k: int = 5
    ):

        query_embedding = (
            EmbeddingService
            .generate_embedding(
                query
            )
        )

        statement = (
            select(DocumentChunk)
            .join(
                ChunkEmbedding,
                ChunkEmbedding.chunk_id
                == DocumentChunk.chunk_id
            )
            .where(
                DocumentChunk.doc_id
                == document_id
            )
            .order_by(
                ChunkEmbedding.embedding
                .cosine_distance(
                    query_embedding
                )
            )
            .limit(top_k)
        )

        chunks = (
            session
            .exec(statement)
            .all()
        )

        return chunks