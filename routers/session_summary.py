from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.session_summary import SessionSummary
from schemas.session_summary import(
    SessionSummaryCreate,
    SessionSummaryRead
)

router=APIRouter(
    prefix="/session_summary",
    tags=["SessionSummary"]
)


@router.get("", response_model=list[SessionSummaryRead])
def read_session_summaries(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    session_summary= (
        session.exec(
            select(SessionSummary)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return session_summary

@router.get("/{session_summary_id}",
            response_model=SessionSummaryRead)
def read_session_summary(
    session_summary_id: UUID,
    session: SessionDep
):
    session_summary = session.get(SessionSummary, session_summary_id)

    if not session_summary:
        raise HTTPException(
            status_code=404,
            detail="Session Summary not found"
        )

    return session_summary


@router.delete("/{session_summary_id}")
def delete_session_summary(
    session_summary_id: UUID,
    session: SessionDep
):
    session_summary = session.get(
        SessionSummary,
        session_summary_id
    )

    if not session_summary:
        raise HTTPException(
            status_code=404,
            detail="Session Summary not found"
        )

    session.delete(session_summary)

    session.commit()

    return {"ok": True}