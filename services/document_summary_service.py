from sqlmodel import Session

from models.document_summary import (
    DocumentSummary
)

from services.llm_service import (
    LLMService
)


class DocumentSummaryService:

    @staticmethod
    def generate_summary(
        doc_id,
        markdown_content: str,
        session: Session
    ):
        


        prompt = f"""
You are a senior financial analyst.

Analyze the following financial document and generate a professional executive summary suitable for a financial intelligence dashboard.

Generate the summary in the following structure:

## Company Overview
Provide a brief description of the company, business model, products, services, and market position.

## Financial Performance
Summarize revenue, profitability, growth trends, margins, operating performance, and any important financial indicators mentioned.

## Strategic Priorities
Describe management objectives, investments, expansion plans, transformation initiatives, acquisitions, partnerships, or future plans.

## Risks and Challenges
Highlight major risks, uncertainties, operational concerns, regulatory issues, competitive threats, or market challenges.

## Key Highlights
List the most important achievements, announcements, milestones, or notable developments.

## Executive Takeaway
Provide a concise 3-5 sentence assessment of the overall health, direction, and outlook of the company.

Requirements:
- Be factual and objective.
- Do not invent information.
- If a section is not present in the document, explicitly state that sufficient information was not available.
- Use concise professional language.
- Focus on information relevant to investors, analysts, and finance teams.

Document:

{markdown_content[:12000]}
"""
        print("STARTING SUMMARY GENERATION", flush=True)

        print(
            f"Markdown length: {len(markdown_content)}",
            flush=True
        )

        print(
            f"Prompt length: {len(prompt)}",
            flush=True
        )

        summary = (
            LLMService.generate_response(
                prompt
            )
        )

        print("LLM RESPONSE RECEIVED", flush=True)

        document_summary = (
            DocumentSummary(
                doc_id=doc_id,
                content=summary,
                model_used="nvidia",
                key_metrics={}
            )
        )

        print("SAVING SUMMARY TO DATABASE", flush=True)
        
        session.add(document_summary)

        session.commit()

        print("SUMMARY SAVED", flush=True)

        session.refresh(
            document_summary
        )

        return document_summary