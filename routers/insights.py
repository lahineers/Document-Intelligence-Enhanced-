from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.insights import Insights
from sqlalchemy.exc import IntegrityError
from schemas.insights import(
    InsightsCreate,
    InsightRead,
    InsightUpdate
)

router=APIRouter(
    prefix="/insights",
    tags=["Insights"]
)

@router.post("", response_model=InsightRead)
def create_insights(
    insight_data: InsightsCreate,
    session: SessionDep
):
    insight = Insights(
        doc_id=insight_data.doc_id,
        session_id=insight_data.session_id,
        model_used=insight_data.model_used,
        scope=insight_data.scope
    )

    try:
        session.add(insight)
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to add Insight"
        )

    session.refresh(insight)

    return insight

@router.get("", response_model=list[InsightRead])
def read_insights(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    insight = (
        session.exec(
            select(Insights)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return insight

@router.get("/{insight_id}",
            response_model=InsightRead)
def read_insight(
    insight_id: UUID,
    session: SessionDep
):
    insight = session.get(Insights, insight_id)

    if not insight:
        raise HTTPException(
            status_code=404,
            detail="Insight not found"
        )

    return insight

@router.patch("/{insight_id}",
              response_model=InsightRead)
def update_insight(
    insight_id: UUID,
    insight_update: InsightUpdate,
    session: SessionDep
):
    insight = session.get(Insights, insight_id)

    if not insight:
        raise HTTPException(
            status_code=404,
            detail="Insight not found"
        )

    update_data = insight_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(insight, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to update insight"
        )

    session.refresh(insight)

    return insight

@router.delete("/{insight_id}")
def delete_insight(
    insight_id: UUID,
    session: SessionDep
):
    insight = session.get(
        Insights,
        insight_id
    )

    if not insight:
        raise HTTPException(
            status_code=404,
            detail="Insight not found"
        )

    session.delete(insight)

    session.commit()

    return {"ok": True}