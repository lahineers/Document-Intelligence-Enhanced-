from sqlmodel import Session, select

from models.chunk_embedding import ChunkEmbedding
from models.document_chunk import DocumentChunk

from services.embedding_service import (
    EmbeddingService
)

from core.settings import settings


class ChunkEmbeddingService:

    @staticmethod
    def get_embedding_by_chunk(
        chunk_id,
        session: Session
    ):

        return (
            session.exec(
                select(ChunkEmbedding)
                .where(
                    ChunkEmbedding.chunk_id
                    == chunk_id
                )
            )
            .first()
        )

    @staticmethod
    def create_embeddings_for_document(
        doc_id,
        session: Session
    ):

        chunks = (
            session.exec(
                select(DocumentChunk)
                .where(
                    DocumentChunk.doc_id
                    == doc_id
                )
            )
            .all()
        )

        pending_chunks = [
            chunk
            for chunk in chunks
            if chunk.embedding_status
            != "completed"
        ]

        if not pending_chunks:

            return []

        texts = [
            chunk.chunk_text
            for chunk in pending_chunks
        ]

        embedding_vectors = (
            EmbeddingService
            .generate_embeddings_batch(
                texts
            )
        )

        embeddings = []

        for chunk, embedding_vector in zip(
            pending_chunks,
            embedding_vectors
        ):

            embedding = ChunkEmbedding(
                chunk_id=chunk.chunk_id,
                embedding=embedding_vector,
                model_name=settings.embedding_model
            )

            session.add(
                embedding
            )

            chunk.embedding_status = (
                "completed"
            )

            embeddings.append(
                embedding
            )

        session.commit()

        return embeddings