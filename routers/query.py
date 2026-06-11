from fastapi import APIRouter

from db import SessionDep

from schemas.query import (
    QueryRequest,
    QueryCreate
)

from services.query_service import QueryService

from agents.analysis_agent import AnalysisAgent
from agents.orchestrator_agent import OrchestratorAgent

from agents.memory_agent import MemoryAgent


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


@router.post("")
def ask_question(
    request: QueryRequest,
    session: SessionDep
):
    
    memory_context = (
        MemoryAgent
        .build_context(
            session
        )
    )

    print(memory_context)

    result = (
        OrchestratorAgent
        .handle_request(
            request.query,
            request.document_id,
            session
        )
    )

    answer = result["answer"]

    chunks = result["sources"]

    QueryService.create_query(
        QueryCreate(
            question=request.query,
            answer=answer
        ),
        session
    )

    return {
        "answer": answer,
        "sources": [
            {
                "chunk_id":
                str(chunk.chunk_id),

                "heading":
                chunk.heading
            }
            for chunk in chunks
        ]
    }