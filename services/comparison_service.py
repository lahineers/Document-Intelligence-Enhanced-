from services.retrieval_service import (
    RetrievalService
)

from services.llm_service import (
    LLMService
)


class ComparisonService:

    @staticmethod
    def compare_documents(
        question,
        document_ids,
        session
    ):

        document_contexts = []
        
        print("starting comparison")

        for document_id in document_ids:

            print(f"retrieving documents: {document_id}")

            chunks = (
                RetrievalService
                .retrieve_chunks(
                    query=question,
                    document_id=document_id,
                    session=session,
                    top_k=2
                )
            )

            print(
                f"Retrieved {len(chunks)} chunks"
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


        print(
            f"Prompt length: {len(prompt)}"
        )

        print(
            "Calling LLM"
        )

        return (
            LLMService
            .generate_response(
                prompt
            )
        )