from sqlmodel import Session

from models.document import Document

from services.PDFExtractionService import PDFExtractionService
from services.chunking_service import ChunkingService
from services.document_chunk_service import DocumentChunkService
from services.chunk_embedding_service import ChunkEmbeddingService


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

        print(
            f"Starting ingestion for {doc_id}"
        )

        markdown_content = (
            PDFExtractionService
            .extract_markdown(
                document.doc_path
            )
        )

        print(markdown_content[:3000])

        markdown_content = (
            markdown_content
            .replace("￾", "")
        )

        print(
            "Markdown extraction completed"
        )

        chunks = (
            ChunkingService
            .chunk_document(
                markdown_content
            )
        )

        print(
            f"Created {len(chunks)} chunks"
        )

        DocumentChunkService.create_chunks_for_document(
            doc_id,
            chunks,
            session
        )

        print(
            "Chunks stored"
        )

        embeddings = (
            ChunkEmbeddingService
            .create_embeddings_for_document(
                doc_id,
                session
            )
        )

        print(
            f"Created {len(embeddings)} embeddings"
        )

        return {
            "chunks_created": len(chunks),
            "embeddings_created": len(embeddings)
        }