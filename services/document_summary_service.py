from sqlmodel import Session, select

from models.document_chunk import DocumentChunk
from models.document_summary import DocumentSummary

from services.llm_service import LLMService


class DocumentSummaryService:

    @staticmethod
    def generate_summary(
        doc_id,
        session: Session
    ):

        chunks = (
            session.exec(
                select(DocumentChunk)
                .where(
                    DocumentChunk.doc_id == doc_id
                )
            )
            .all()
        )

        if not chunks:
            raise Exception(
                "No chunks found for document"
            )

        document_text = "\n".join(
            chunk.chunk_text
            for chunk in chunks
        )

        prompt = f"""
Create a concise executive summary of this financial document.

Focus on:
- Business overview
- Financial performance
- Important highlights
- Key risks if present

Document:

{document_text[:12000]}
"""

        summary = (
            LLMService.generate_response(
                prompt
            )
        )

        document_summary = (
            DocumentSummary(
                doc_id=doc_id,
                content=summary,
                model_used="nvidia",
                key_metrics={}
            )
        )

        session.add(
            document_summary
        )

        session.commit()

        session.refresh(
            document_summary
        )

        return document_summary