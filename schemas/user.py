from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    username:str=Field(
        min_length=5,
        max_length=50
    )
    email:EmailStr
    password:str=Field(
        min_length=8,
        max_length=100
    )

class UserRead(SQLModel):
    user_id:UUID
    username: str
    email:str
    plan:str
    created_at: datetime

class UserUpdate(SQLModel):
    username: Optional[str]=None
    email: Optional[str]=None