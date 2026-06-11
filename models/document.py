from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional,Dict,Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Document(SQLModel, table=True):
    __tablename__="Document"

    doc_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    user_id:UUID=Field(
        foreign_key="User.user_id"
    )
    session_id:UUID=Field(
        foreign_key="UploadSession.session_id"
    )
    doc_type: str
    file_name: str
    file_type: str
    doc_path:str
    page_count:int=0
    file_size_bytes: int = 0
    upload_time: datetime=Field(
        default_factory=datetime.utcnow
    )
    extracted_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    processing_status: str="pending"
    
    processed_at:Optional[datetime]=None
 