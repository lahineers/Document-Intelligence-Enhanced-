from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.user import User
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from schemas.user import(
    UserCreate,
    UserRead,
    UserUpdate
)
import logging
logger=logging.getLogger(__name__)

router=APIRouter(
    prefix="/users",
    tags=["User"]
)

password_hash = PasswordHash.recommended()

@router.post("", response_model=UserRead)
def create_user(
    user_data: UserCreate,
    session: SessionDep
):
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=password_hash.hash(user_data.password),
        plan="free"
    )
    try:   
        session.add(user)
        session.commit()
    except IntegrityError:
        logger.info("User creation Error"),
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    
    session.refresh(user)

    return user

@router.get("", response_model=list[UserRead])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = (
        session.exec(
            select(User)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return users

@router.get("/{user_id}",
            response_model=UserRead)
def read_user(
    user_id: UUID,
    session: SessionDep
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    session: SessionDep
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    update_data = user_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(user, key, value)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.info("User Updation FAILED")

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    session.refresh(user)

    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    session: SessionDep
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    session.delete(user)

    session.commit()

    return {"ok": True}