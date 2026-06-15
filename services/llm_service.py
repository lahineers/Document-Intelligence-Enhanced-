from openai import OpenAI
from opentelemetry import trace

from core.settings import settings

tracer = trace.get_tracer(__name__)


class LLMService:

    _client = None

    @classmethod
    def _get_client(cls):

        if cls._client is None:

            cls._client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=settings.nvidia_api_key
            )

        return cls._client

    @classmethod
    def generate_response(
        cls,
        prompt: str
    ) -> str:

        client = cls._get_client()

        with tracer.start_as_current_span(
            "llm_generation"
        ) as span:

            span.set_attribute(
                "llm.provider",
                "nvidia"
            )

            span.set_attribute(
                "llm.model",
                settings.llm_model
            )

            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )

            if (
                hasattr(response, "usage")
                and response.usage
            ):

                span.set_attribute(
                    "llm.prompt_tokens",
                    response.usage.prompt_tokens
                )

                span.set_attribute(
                    "llm.completion_tokens",
                    response.usage.completion_tokens
                )

                span.set_attribute(
                    "llm.total_tokens",
                    response.usage.total_tokens
                )

            return (
                response
                .choices[0]
                .message
                .content
            )

    @classmethod
    def answer_question(
        cls,
        question: str,
        context_chunks: list[dict],
        memory_context: str = ""
    ) -> str:

        context = "\n\n".join(
            [
                chunk["content"]
                for chunk in context_chunks
            ]
        )

        prompt = f"""
You are a document analysis assistant.

Use the previous conversation when it is relevant.

Use only the provided document context for factual information.

Provide a complete answer.

Do not stop after one item.

If the answer contains a list, include every item found in the context.

If the information is not available in the document context, say so.

Previous Conversation:
{memory_context}

Document Context:
{context}

Question:
{question}

Answer:
"""

        return cls.generate_response(
            prompt
        )