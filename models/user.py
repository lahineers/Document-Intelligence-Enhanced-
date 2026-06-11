from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__="User"

    user_id: UUID=Field(
        default_factory=uuid4,
        primary_key=True,
    )
    username:str=Field(unique=True,index=True)

    email:str=Field(unique=True, index=True)

    hashed_password:str

    plan:str

    created_at: datetime=Field(
        default_factory=datetime.utcnow
    )

    last_login: Optional[datetime]=None
