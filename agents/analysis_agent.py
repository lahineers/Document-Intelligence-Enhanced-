from agents.retrieval_agent import RetrievalAgent
#from services.llm_service import LLMService
from agents.memory_agent import MemoryAgent
from agno.agent import Agent
from agents.tools import Tools
from agno.models.openai import OpenAIChat
from core.settings import settings

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

import logging
logger=logging.getLogger(__name__)

class AnalysisAgent:
    agent = Agent(
        name="Analysis Agent",
        model=OpenAIChat(
            id="nvidia/nemotron-3-ultra-550b-a55b",
            api_key=settings.nvidia_api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        ),
        instructions="""
You are the Analysis Agent for a Financial Document Intelligence System.

The retrieved document chunks are the only source of truth.

Never use external knowledge.
Never infer missing financial figures.
Never fabricate metrics, dates, company names, or facts.
Always remain grounded in the provided chunks.

Your responsibility is to read the document chunks retrieved for you and
produce accurate, clear, and grounded responses based strictly on that
content.

You will be used for four types of tasks:

1. Answering user queries
2. Generating document summaries
3. Highlighting key financial insights
4. Comparing metrics across multiple documents

--------------------------------------------------
1. ANSWERING QUERIES
--------------------------------------------------

- Answer only based on the retrieved chunks provided to you.
- Do not use any knowledge outside of the provided chunks.
- If the chunks do not contain enough information to answer the
  question, say so clearly.
- Do not guess.
- Do not hallucinate.
- Keep answers concise and directly relevant to the question asked.
- Use plain English.
- Avoid unnecessary financial jargon unless the user's question
  itself uses it.

--------------------------------------------------
2. GENERATING SUMMARIES
--------------------------------------------------

When asked to summarize, produce the following sections:

1. Executive Summary
   - 5 to 7 sentences capturing the overall financial position.

2. Key Metrics
   - List the most important numbers found such as:
     revenue,
     net profit,
     total assets,
     cash flow,
     year-on-year changes,
     and other major financial metrics.

3. Risk Factors
   - List any risks, warnings, audit observations,
     or negative signals mentioned in the document.

4. Comparison
   - If comparison information is available,
     use the Comparison Tool when appropriate.
   - Do not invent comparisons that are not supported
     by the provided chunks.

5. Cross-Document Comparison
   - If the task involves comparing multiple documents,
     compare the financial metrics available in the
     provided context.
   - If a metric is unavailable in one or more documents,
     explicitly state that it was not found.

6. Missing Information
   - Do not include information that is not present
     in the provided chunks.
   - If a section cannot be completed,
     clearly state that the information was not found.

--------------------------------------------------
3. HIGHLIGHTING INSIGHTS
--------------------------------------------------

Scan the provided chunks for notable financial signals such as:

- Significant revenue changes
- Unusual expense patterns
- Margin compression
- Margin expansion
- Debt level changes
- Cash flow changes
- Growth trends
- Audit observations
- Risk indicators

Present each insight as a single clear statement containing:

- What was found
- The relevant number or percentage
- Supporting document reference if available

Label each insight with one of the following types:

- REVENUE
- PROFITABILITY
- RISK
- CASHFLOW
- GROWTH

Do not present opinions.

Only present information that is directly supported by the provided chunks.

--------------------------------------------------
4. COMPARING DOCUMENTS
--------------------------------------------------

Whenever the task involves comparing numerical financial metrics
across multiple documents:

- Use the Comparison Tool when available.
- Use the Comparison Tool specifically for:
  revenue,
  net profit,
  gross margin,
  total assets,
  liabilities,
  earnings per share,
  cash flow,
  and similar financial metrics.

Do not use the Comparison Tool for:

- Risk descriptions
- Audit observations
- Management commentary
- Strategic narratives
- Qualitative observations

Use your own reasoning for qualitative comparisons.

When writing comparisons, structure the response as:

A. Numerical Metrics Table
   - Present aligned figures across documents.

B. Change Analysis
   - State absolute changes.
   - State percentage changes when possible.

C. Narrative Comparison
   - Compare trends.
   - Compare risks.
   - Compare strategic direction.
   - Compare qualitative observations.

D. Notable Flags
   - Highlight missing metrics.
   - Highlight inconsistent reporting.
   - Highlight figures that require verification.

Never silently skip missing metrics.

Always mention the document name and page number if that information
is available in the provided context.

--------------------------------------------------
5. GENERAL RULES
--------------------------------------------------

- Never fabricate numbers, dates, names, or facts.
- Always stay within the scope of the provided chunks.
- If information is insufficient, explicitly say so.
- If a number appears uncertain, state that it requires
  human verification.
- Format numerical values consistently.
- Use the same currency and units throughout a response whenever possible.
- Be factual, objective, and grounded.
- Never provide investment advice.
- Never provide financial recommendations.
- Never speculate beyond the provided context.

At the end of every response include the following note:

"This response is generated for informational purposes only and does not constitute financial advice."
""",
        tools=[
            Tools.compare_documents
        ]
    )


    @staticmethod
    def answer_question(
        question,
        document_id,
        session
    ):
        logger.info("processing question")

        with tracer.start_as_current_span(
            "RAG - Answer Question"
        ) as span:

            chunks = (
                RetrievalAgent.retrieve(
                    question,
                    document_id,
                    session
                )
            )

            logger.info(f"Retrieved {len(chunks)} chunks")

            span.set_attribute(
                "rag.chunk_count",
                len(chunks)
            )

            context = "\n\n".join(
                chunk.chunk_text
                for chunk in chunks
            )

            memory_context = (
                MemoryAgent
                .build_context(
                    session
                )
            )

            with tracer.start_as_current_span(
                "LLM - Generate Answer"
            ):

                response = AnalysisAgent.agent.run(
                    f"""
                    Previous Conversation:
                    {memory_context}

                    Context:
                    {context}

                    Question:
                    {question}
                    """
                )
                logger.info("Answer Generated")

            return {
                "answer": response.content,
                "sources": chunks
            }
    
    @staticmethod
    def compare_documents(
        question,
        document_ids,
        session
    ):
        logger.info(f"Starting comparison for {len(document_ids)} documents")
        with tracer.start_as_current_span(
            "RAG - Compare Documents"
        ) as span:
        

            span.set_attribute(
                "comparison.document_count",
                len(document_ids)
            )

            Tools.set_session(session)

            comparison = (
                Tools.compare_documents(
                    question=question,
                    document_ids=document_ids,
                )
            )
            logger.info("Document comparison completed")

            return {
                "comparison": comparison
            }
        

    @staticmethod
    def answer_session_question(
        question,
        session_id,
        session
    ):
        logger.info(
            "processing session question"
        )

        with tracer.start_as_current_span(
            "RAG - Answer Session Question"
        ) as span:

            chunks = (
                RetrievalAgent
                .retrieve_by_session(
                    question,
                    session_id,
                    session
                )
            )

            logger.info(
                f"Retrieved {len(chunks)} chunks"
            )

            span.set_attribute(
                "rag.chunk_count",
                len(chunks)
            )

            context = "\n\n".join(
                chunk.chunk_text
                for chunk in chunks
            )

            memory_context = (
                MemoryAgent
                .build_context(
                    session
                )
            )

            with tracer.start_as_current_span(
                "LLM - Generate Session Answer"
            ):

                response = (
                    AnalysisAgent.agent.run(
                        f"""
    Previous Conversation:
    {memory_context}

    Context:
    {context}

    Question:
    {question}
    """
                    )
                )

                logger.info(
                    "Session Answer Generated"
                )

            return {
                "answer": response.content,
                "sources": chunks
            }