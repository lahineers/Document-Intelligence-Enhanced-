from fastapi import APIRouter

from db import SessionDep

from schemas.comparison import (
    ComparisonRequest
)

from agents.analysis_agent import (
    AnalysisAgent
)


router = APIRouter(
    prefix="/comparison",
    tags=["Comparison"]
)


@router.post("")
def compare_documents(
    request: ComparisonRequest,
    session: SessionDep
):

    result = (
        AnalysisAgent
        .compare_documents(
            question=request.question,
            document_ids=request.document_ids,
            session=session
        )
    )

    return result