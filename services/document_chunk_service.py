from sqlmodel import Session, select

from models.document_chunk import DocumentChunk
from schemas.document_chunk import DocumentChunkCreate


class DocumentChunkService:

    @staticmethod
    def create_chunk(
        chunk_data: DocumentChunkCreate,
        session: Session
    ) -> DocumentChunk:

        chunk = DocumentChunk(
            **chunk_data.model_dump()
        )

        session.add(chunk)
        session.commit()
        session.refresh(chunk)

        return chunk

    @staticmethod
    def get_chunk(
        chunk_id,
        session: Session
    ):

        return session.get(
            DocumentChunk,
            chunk_id
        )

    @staticmethod
    def get_chunks_by_document(
        doc_id,
        session: Session
    ):

        return session.exec(
            select(DocumentChunk)
            .where(
                DocumentChunk.doc_id == doc_id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
        ).all()

    @staticmethod
    def delete_chunks_by_document(
        doc_id,
        session: Session
    ):

        chunks = session.exec(
            select(DocumentChunk)
            .where(
                DocumentChunk.doc_id == doc_id
            )
        ).all()

        for chunk in chunks:
            session.delete(chunk)

        session.commit()

    @staticmethod
    def create_chunks_for_document(
        doc_id,
        chunks,
        session: Session
    ):

        created_chunks = []

        for chunk in chunks:

            payload = DocumentChunkCreate(
                doc_id=doc_id,
                heading=(
                    chunk.get("section_title")[:100]
                    if chunk.get("section_title")
                    else None
                ),
                chunk_text=chunk.get(
                    "content"
                ),
                chunk_index=chunk.get(
                    "chunk_index"
                ),
                page_number=0
            )

            created_chunk = (
                DocumentChunkService
                .create_chunk(
                    payload,
                    session
                )
            )

            created_chunks.append(
                created_chunk
            )

        return created_chunks