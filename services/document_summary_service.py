from sqlmodel import Session
from sqlmodel import select

from models.document_chunk import DocumentChunk

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

from models.document_summary import (
    DocumentSummary
)

from services.llm_service import (
    LLMService
)


class DocumentSummaryService:

    @staticmethod
    def summarize_chunk(
        heading: str,
        page_number: int,
        chunk_text: str
    ) -> str:

        prompt = f"""
        You are a senior financial analyst.

        Summarize the following section.

        Section Heading:
        {heading}

        Page Number:
        {page_number}

        Return the result in this format:

        ## {heading}

        - Important point 1
        - Important point 2
        - Important point 3

        Rules:
        - Maximum 5 bullet points.
        - Maximum 100 words total.
        - Focus on financial metrics, business performance, strategy and risks.
        - Do not explain.
        - Do not repeat information.
        - Do not invent facts.
        - If nothing important is present, write:
        - No significant information found.

        Section Content:

        {chunk_text}
        """


        return (
                LLMService.generate_response(
                    prompt
                )
            )

    @staticmethod
    def generate_summary(
        doc_id,
        markdown_content: str,
        session: Session
    ):

       
        chunks = (
            session.exec(
                select(DocumentChunk)
                .where(
                    DocumentChunk.doc_id == doc_id
                )
                .order_by(
                    DocumentChunk.chunk_index
                )
            )
            .all()
        )

        if not chunks:
            raise ValueError(
                f"No chunks found for document {doc_id}"
            )

        print(
            f"Found {len(chunks)} chunks",
            flush=True
        )

        chunk_summaries=[]

        for i, chunk in enumerate(chunks):

            print(
                f"Summarizing chunk {i + 1}/{len(chunks)}",
                flush=True
            )
            

            try:
                chunk_summary = (
                    DocumentSummaryService
                    .summarize_chunk(
                        heading=chunk.heading,
                        page_number=chunk.page_number,
                        chunk_text=chunk.chunk_text
                    )
                )

                chunk_summaries.append(
                    chunk_summary
                )

                print(
                    f"Chunk Summary Length: {len(chunk_summary)}",
                    flush=True
                )
            
            except Exception as e:
                print(
                    f"Chunk {i+1} failed: {e}",
                    flush=True
                )

        
        combined_summary = "\n\n".join(
            chunk_summaries
        )

       
        print(
            f"Combined Summary Length: {len(combined_summary)}",
            flush=True
        )

        print(
            combined_summary[:2000],
            flush=True
        )

        with tracer.start_as_current_span(
            "summary_generation"
        ) as span:

            span.set_attribute(
                "document.id",
                str(doc_id)
            )

            span.set_attribute(
                "markdown.length",
                len(markdown_content)
            )

            if not chunk_summaries:
                raise ValueError(
                    f"No chunk summaries generated for document {doc_id}"
                )

            summary=combined_summary

            print(
                f"SUMMARY LENGTH: {len(summary)}",
                flush=True
            )

            print(
                "SUMMARY PREVIEW:",
                flush=True
            )

            print(
                summary[:1000],
                flush=True
            )

            span.add_event(
                "llm_response_received"
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

            span.add_event(
                "summary_saved"
            )

            span.set_attribute(
                "summary.length",
                len(summary)
            )

            session.refresh(
                document_summary
            )

            return document_summary