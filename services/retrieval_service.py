from sqlmodel import Session, select
from uuid import UUID
from models.document_chunk import DocumentChunk
from models.chunk_embedding import ChunkEmbedding
from models.document import Document

from services.embedding_service import EmbeddingService

from opentelemetry import trace
tracer=trace.get_tracer(__name__)


class RetrievalService:

    @staticmethod
    def retrieve_chunks(
        query: str,
        document_id:UUID,
        session: Session,
        top_k: int = 5
    ):
        with tracer.start_as_current_span("RAG-Generate Query Embedding"):
            query_embedding = (
                EmbeddingService
                .generate_embedding(
                    query
                )
            )

        with tracer.start_as_current_span("RAG-Retrieve Chunks") as span:
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

            span.set_attribute(
                "retrieval.chunk_count",
                len(chunks)
            )

            span.set_attribute(
                "retrieval.top_k",
                top_k
            )


        return chunks
    
    @staticmethod
    def retrieve_chunks_by_session(
        query: str,
        session_id: UUID,
        session: Session,
        top_k: int = 5
    ):
        with tracer.start_as_current_span(
            "RAG-Generate Query Embedding"
        ):
            query_embedding = (
                EmbeddingService
                .generate_embedding(
                    query
                )
            )

        with tracer.start_as_current_span(
            "RAG-Retrieve Session Chunks"
        ) as span:

            statement = (
                select(DocumentChunk)
                .join(
                    ChunkEmbedding,
                    ChunkEmbedding.chunk_id
                    == DocumentChunk.chunk_id
                )
                .join(
                    Document,
                    Document.doc_id
                    == DocumentChunk.doc_id
                )
                .where(
                    Document.session_id
                    == session_id
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

            span.set_attribute(
                "retrieval.chunk_count",
                len(chunks)
            )

            span.set_attribute(
                "retrieval.top_k",
                top_k
            )

            span.set_attribute(
                "retrieval.session_id",
                str(session_id)
            )

        return chunks