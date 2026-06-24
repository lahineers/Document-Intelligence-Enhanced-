from openai import OpenAI
import time
from core.settings import settings
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=settings.nvidia_api_key,
    timeout=60
)

start = time.time()

try:

    response = client.chat.completions.create(
        model="google/gemma-3-4b-it",
        messages=[
            {
                "role": "user",
                "content": "Say hello."
            }
        ],
        max_tokens=10
    )

    print(
        f"Completed in {time.time() - start:.2f}s"
    )

    print(
        response.choices[0].message.content
    )

except Exception as e:

    print(type(e).__name__)
    print(e)