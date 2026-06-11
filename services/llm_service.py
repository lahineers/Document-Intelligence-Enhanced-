from openai import OpenAI
from datetime import datetime

from core.settings import settings


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

        print(
            f"[{datetime.now()}] STEP 1: Client created"
        )

        start = datetime.now()

        print(
            f"[{start}] STEP 2: Calling NVIDIA"
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

        end = datetime.now()

        print(
            f"[{end}] STEP 3: Response received"
        )
        print(
            response.choices[0].message.content
        )

        print(
            f"NVIDIA call took: "
            f"{(end - start).total_seconds():.2f}s"
        )

        return (
            response.choices[0].message.content
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