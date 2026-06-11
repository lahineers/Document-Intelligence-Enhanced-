from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.messages import Messages
from sqlalchemy.exc import IntegrityError
from schemas.messages import(
    MessagesCreate,
    MessagesRead,
    MessagesUpdate
)

router=APIRouter(
    prefix="/messages",
    tags=["Messages"]
)

@router.post("", response_model=MessagesRead)
def create_message(
    message_data: MessagesCreate,
    session: SessionDep
):
    message = Messages(
        query_session_id=message_data.query_session_id,
        role=message_data.role,
        content=message_data.content,
        tools_calls=message_data.tools_calls,
        tokens_used=message_data.tokens_used
    )

    try:
        session.add(message)
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to add Message"
        )

    session.refresh(message)

    return message

@router.get("", response_model=list[MessagesRead])
def read_messages(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    message = (
        session.exec(
            select(Messages)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return message

@router.get("/{message_id}",
            response_model=MessagesRead)
def read_message(
    message_id: UUID,
    session: SessionDep
):
    message = session.get(Messages, message_id)

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    return message

@router.patch("/{message_id}",
              response_model=MessagesRead)
def update_message(
    message_id: UUID,
    message_update: MessagesUpdate,
    session: SessionDep
):
    message = session.get(Messages, message_id)

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    update_data = message_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(message, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to update message"
        )

    session.refresh(message)

    return message

@router.delete("/{message_id}")
def delete_message(
    message_id: UUID,
    session: SessionDep
):
    message = session.get(
        Messages,
        message_id
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    session.delete(message)

    session.commit()

    return {"ok": True}