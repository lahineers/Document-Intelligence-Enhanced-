from sqlmodel import Session

from models.document import Document
from services.minio_service import minio_service
from services.PDFExtractionService import PDFExtractionService
from services.chunking_service import ChunkingService
from services.document_chunk_service import DocumentChunkService
from services.chunk_embedding_service import ChunkEmbeddingService

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

import logging 
logger=logging.getLogger(__name__)

class IngestionService:

    @staticmethod
    def ingest_document(
        doc_id,
        session: Session
    ):

        document = session.get(
            Document,
            doc_id
        )

        if not document:
            raise ValueError(
                f"Document not found: {doc_id}"
            )
        
        logger.info("Starting document ingestion")

        with tracer.start_as_current_span(
            "pdf_extraction"
        ) as span:
            pdf_bytes = (
                minio_service.download_bytes(
                    document.doc_path
                )
            )

            span.set_attribute(
                "pdf.size_bytes",
                len(pdf_bytes)
            )

            markdown_content = (
                PDFExtractionService
                .extract_markdown_from_bytes(
                    pdf_bytes
                )
            )

        markdown_content = (
            markdown_content
            .replace("￾", "")
        )

        markdown_key = (
            f"extracted/{document.doc_id}.md"
        )

        minio_service.upload_text(
            markdown_content,
            markdown_key
        )

        document.markdown_object_key = (
            markdown_key
        )

        session.add(document)
        session.commit()

        with tracer.start_as_current_span(
            "chunk_generation"
        ) as span:

            chunks = (
                ChunkingService
                .chunk_document(
                    markdown_content
                )
            )

            span.set_attribute(
                "chunk.count",
                len(chunks)
            )

            logger.info(
                f"Chunk generation complete"
                f"chunks created:{len(chunks)}"
            )

        with tracer.start_as_current_span(
            "chunk_storage"
        ):

            DocumentChunkService.create_chunks_for_document(
                doc_id,
                chunks,
                session
            )

        with tracer.start_as_current_span(
            "embedding_generation"
        ) as span:

            embeddings = (
                ChunkEmbeddingService
                .create_embeddings_for_document(
                    doc_id,
                    session
                )
            )

            span.set_attribute(
                "embedding.count",
                len(embeddings)
            )
            logger.info(
                f"Embedding generation complete"
                f"Embeddings created: {len(embeddings)}"
            )
        
        logger.info(
            f"Document Ingestion complete"
            f"Chunks: {len(chunks)}"
            f"Embeddings: {len(embeddings)}"
        )

        return {
            "chunks_created": len(chunks),
            "embeddings_created": len(embeddings)
        }