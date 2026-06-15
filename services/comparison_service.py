from services.retrieval_service import RetrievalService
from services.llm_service import LLMService

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class ComparisonService:

    @staticmethod
    def compare_documents(
        question,
        document_ids,
        session
    ):

        with tracer.start_as_current_span(
            "document_comparison"
        ) as span:

            span.set_attribute(
                "comparison.document_count",
                len(document_ids)
            )

            document_contexts = []

            for document_id in document_ids:

                chunks = (
                    RetrievalService
                    .retrieve_chunks(
                        query=question,
                        document_id=document_id,
                        session=session,
                        top_k=2
                    )
                )

                context = "\n\n".join(
                    chunk.chunk_text
                    for chunk in chunks
                )

                document_contexts.append(
                    {
                        "document_id":
                        str(document_id),

                        "context":
                        context
                    }
                )

            comparison_context = ""

            for index, doc in enumerate(
                document_contexts,
                start=1
            ):

                comparison_context += (
                    f"\n\n"
                    f"DOCUMENT {index}\n"
                    f"{doc['context']}"
                )

            prompt = f"""
You are a document comparison expert.

Compare the documents using ONLY
the provided context.

Question:
{question}

Documents:
{comparison_context}

Provide:

1. Key similarities

2. Key differences

3. Important insights

4. Final summary
"""

            span.set_attribute(
                "comparison.prompt_length",
                len(prompt)
            )

            return (
                LLMService
                .generate_response(
                    prompt
                )
            )