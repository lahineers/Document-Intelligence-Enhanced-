from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.upload_session import UploadSession
from sqlalchemy.exc import IntegrityError
from schemas.upload_session import(
    UploadSessionCreate,
    UploadSessionRead,
    UploadSessionUpdate
)

import logging
logger=logging.getLogger(__name__)

router=APIRouter(
    prefix="/upload_session",
    tags=["Upload Session"]
)

@router.post("", response_model=UploadSessionRead)
def create_upload_session(
    upload_session_data: UploadSessionCreate,
    session: SessionDep
):
    upload_session = UploadSession(
        user_id=upload_session_data.user_id,
        title=upload_session_data.title
    )
    try:   
        session.add(upload_session)
        session.commit()
    except IntegrityError:
        logger.info("Failed to create uplaod session")
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to create upload session"
        )
    
    session.refresh(upload_session)

    return upload_session

@router.get("", response_model=list[UploadSessionRead])
def read_uploadsessions(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    uploadsessions = (
        session.exec(
            select(UploadSession)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return uploadsessions

@router.get("/{session_id}",
            response_model=UploadSessionRead)
def read_upload_session(
    session_id: UUID,
    session: SessionDep
):
    uploadsession = session.get(UploadSession, session_id)

    if not uploadsession:
        raise HTTPException(
            status_code=404,
            detail="Upload Session not found"
        )

    return uploadsession

@router.patch("/{session_id}", response_model=UploadSessionRead)
def update_uploadsession(
    session_id: UUID,
    uploadsession_update: UploadSessionUpdate,
    session: SessionDep
):
    uploadsession = session.get(UploadSession, session_id)

    if not uploadsession:
        raise HTTPException(
            status_code=404,
            detail="Upload Session not found"
        )

    update_data = uploadsession_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(uploadsession, key, value)

    try:
        session.commit()
    except IntegrityError:
        logger.info("Failed to update uplaod session"),
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to update Upload Session"
        )
    session.refresh(uploadsession)

    return uploadsession

@router.delete("/{session_id}")
def delete_uploadsession(
    session_id: UUID,
    session: SessionDep
):
    uploadsession = session.get(UploadSession, session_id)

    if not uploadsession:
        raise HTTPException(
            status_code=404,
            detail="Upload Session not found"
        )

    session.delete(uploadsession)

    session.commit()

    return {"ok": True}