from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.query_session import QuerySession
from sqlalchemy.exc import IntegrityError
from schemas.query_session import(
    QuerySessionCreate,
    QuerySessionRead,
    QuerySessionUpdate
)

router=APIRouter(
    prefix="/query_session",
    tags=["QuerySession"]
)

@router.post("", response_model=QuerySessionRead)
def create_query_session(
    query_session_data: QuerySessionCreate,
    session: SessionDep
):
    query_session = QuerySession(
        session_id=query_session_data.session_id,
        title=query_session_data.title,
    )

    try:
        session.add(query_session)
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to add Query Session"
        )

    session.refresh(query_session)

    return query_session

@router.get("", response_model=list[QuerySessionRead])
def read_query_session(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    query_session = (
        session.exec(
            select(QuerySession)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return query_session

@router.get("/{query_session_id}",
            response_model=QuerySessionRead)
def read_document(
    query_session_id: UUID,
    session: SessionDep
):
    query_session = session.get(QuerySession, query_session_id)

    if not query_session:
        raise HTTPException(
            status_code=404,
            detail="Query Session not found"
        )

    return query_session

@router.patch("/{query_session_id}",
              response_model=QuerySessionRead)
def update_query_session(
    query_session_id: UUID,
    query_session_update: QuerySessionUpdate,
    session: SessionDep
):
    query_session = session.get(QuerySession, query_session_id)

    if not query_session:
        raise HTTPException(
            status_code=404,
            detail="Query Session not found"
        )

    update_data = query_session_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(query_session, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to update query session"
        )

    session.refresh(query_session)

    return query_session

@router.delete("/{query_session_id}")
def delete_document(
    query_session_id: UUID,
    session: SessionDep
):
    query_session = session.get(
        QuerySession,
        query_session_id
    )

    if not query_session:
        raise HTTPException(
            status_code=404,
            detail="Query Session not found"
        )

    session.delete(query_session)

    session.commit()

    return {"ok": True}