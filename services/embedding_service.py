from openai import OpenAI

from core.settings import settings
import time

class EmbeddingService:

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
    def generate_embedding(
        cls,
        text: str
    ) -> list[float]:

        client = cls._get_client()

        response = (
            client.embeddings.create(
                model=settings.embedding_model,
                input=text
            )
        )

        return (
            response
            .data[0]
            .embedding
        )

    @classmethod
    def generate_embeddings_batch(
        cls,
        texts: list[str]
    ) -> list[list[float]]:
        
        #testing:
        print(f"Sending batch of {len(texts)} texts")

        client = cls._get_client()

        #testingh
        start=time.time()

        response = (
            client.embeddings.create(
                model=settings.embedding_model,
                input=texts
            )
        )

        print(
            f"Batch completed in "
            f"{time.time() - start:.2f}s"
        )

        return [
            item.embedding
            for item in response.data
        ]