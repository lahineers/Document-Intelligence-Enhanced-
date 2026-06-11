from sqlmodel import select
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from core.settings import settings
from models.query import Query


class MemoryAgent:

    agent = Agent(
        name="Memory Agent",
        model=OpenAIChat(
            id="nvidia/nemotron-3-ultra-550b-a55b",
            api_key=settings.nvidia_api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        ),
        instructions="""
You are the Memory Agent for a Financial Document Intelligence System.

Your responsibility is to provide relevant conversation history
to other agents when requested.

You do not answer user questions.
You do not analyze documents.
You do not retrieve document content.

Your role is only to manage and provide conversation context.

Rules:

1. Retrieve recent conversation history from the current session.

2. Return the conversation history in chronological order.

3. Preserve user questions and assistant responses exactly as stored.

4. Do not modify, interpret, summarize, or analyze the conversation.

5. Do not generate new information.

6. Return only conversation context that can be used by other agents.

7. Never interact directly with the user.
"""
    )


    @staticmethod
    def get_recent_queries(
        session,
        limit: int = 5
    ):

        queries = (
            session
            .exec(
                select(Query)
                .order_by(
                    Query.created_at.desc()
                )
                .limit(limit)
            )
            .all()
        )

        return queries

    @staticmethod
    def build_context(
        session,
        limit: int = 2
    ):

        

        queries = (
            MemoryAgent
            .get_recent_queries(
                session,
                limit
            )
        )

        print(
            f"Found {len(queries)} queries"
        )

        context = ""

        for query in reversed(queries):

            context += (
                f"\nUser: "
                f"{query.question}\n"
                f"Assistant: "
                f"{query.answer}\n"
            )

        return context