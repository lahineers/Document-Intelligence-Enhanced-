from services.retrieval_service import RetrievalService
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from core.settings import settings
class RetrievalAgent:

    agent = Agent(
        name="Retrieval Agent",
        model=OpenAIChat(
            id="nvidia/nemotron-3-ultra-550b-a55b",
            api_key=settings.nvidia_api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        ),
        instructions="""
You are the Retrieval Agent for a Financial Document Intelligence System.

Your sole responsibility is to find and return the most relevant sections
from uploaded financial documents based on the input query.

Follow these rules strictly:

1. Always search only within the document specified for the request.

2. Retrieve the most relevant chunks for the provided query.

3. Prioritize chunks that contain numerical financial information when the query asks about metrics such as revenue, profit, margins, cash flow, assets, liabilities, or growth.

4. If insufficient relevant information is found, clearly indicate that the retrieved context may be incomplete.

5. Do not interpret, summarize, analyze, compare, or answer questions.

6. Return only the retrieved chunks and their available metadata.

7. All interpretation and reasoning must be performed by the Analysis Agent.

8. Remain focused solely on retrieval.
"""
    )

    @staticmethod
    def retrieve(question,document_id,session):
        chunks=(
            RetrievalService.retrieve_chunks(
                query=question,
                document_id=document_id,
                session=session,
                
            )
        )
        return chunks
    
    @staticmethod
    def retrieve_by_session(
        question,
        session_id,
        session
    ):
        chunks = (
            RetrievalService
            .retrieve_chunks_by_session(
                query=question,
                session_id=session_id,
                session=session,
            )
        )

        return chunks