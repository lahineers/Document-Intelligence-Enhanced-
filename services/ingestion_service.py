from sqlmodel import Session

from models.document import Document

from services.minio_service import minio_service
from services.PDFExtractionService import PDFExtractionService
from services.rabbitmq_service import RabbitMQService

from opentelemetry import trace

import logging

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


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

        document.processing_status = "extracting"
        session.add(document)
        session.commit()

        if not document:
            raise ValueError(
                f"Document not found: {doc_id}"
            )

        logger.info(
            f"Starting extraction for document {doc_id}"
        )

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

        with tracer.start_as_current_span(
            "markdown_storage"
        ) as span:

            minio_service.upload_text(
                markdown_content,
                markdown_key
            )

            span.set_attribute(
                "markdown.object_key",
                markdown_key
            )

        document.markdown_object_key = markdown_key
        document.processing_status = "extracted"
        session.add(document)
        session.commit()

        logger.info(
            f"Markdown stored at {markdown_key}"
        )

        with tracer.start_as_current_span(
            "publish_chunking_job"
        ) as span:

            rabbitmq_service = RabbitMQService()

            rabbitmq_service.publish_message(
                "document.chunking.queue",
                {
                    "document_id": str(doc_id)
                }
            )

            rabbitmq_service.publish_message(
                "document.summary.queue",
                {
                    "document_id": str(doc_id)
                }
            )

            rabbitmq_service.close()

            span.set_attribute(
                "document.id",
                str(doc_id)
            )

            span.set_attribute(
                "queue.name",
                "document.chunking.queue"
            )

        logger.info(
            f"Chunking job published for document {doc_id}"
        )

        logger.info(
            f"Extraction pipeline completed for document {doc_id}"
        )