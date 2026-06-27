from agents.analysis_agent import AnalysisAgent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from core.settings import settings

class OrchestratorAgent:

    agent = Agent(
        name="Orchestrator Agent",
        model=OpenAIChat(
            id="nvidia/nemotron-3-ultra-550b-a55b",
            api_key=settings.nvidia_api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        ),
        instructions="""
You are the Orchestrator Agent for a Financial Document Intelligence System.

Your responsibility is to coordinate the workflow between the available agents.

Available agents:

- Memory Agent
- Retrieval Agent
- Analysis Agent

Responsibilities:

1. Load relevant conversation context when needed.

2. Coordinate retrieval of relevant document content.

3. Pass retrieved content to the Analysis Agent.

4. Coordinate document comparison workflows.

5. Return only the final response.

6. Never expose internal workflow details.

7. Never generate document analysis yourself.
Analysis must always be performed by the Analysis Agent.
"""
    )


    @staticmethod
    def handle_request(
        question,
        document_id,
        session
    ):

        return (
            AnalysisAgent
            .answer_question(
                question,
                document_id,
                session
            )
        )
    
    @staticmethod
    def handle_comparison(
        question,
        document_ids,
        session
    ):

        return (
            AnalysisAgent
            .compare_documents(
                question,
                document_ids,
                session
            )
        )
    
    @staticmethod
    def handle_session_request(
        question,
        session_id,
        session
    ):
        return (
            AnalysisAgent
            .answer_session_question(
                question,
                session_id,
                session
            )
        )