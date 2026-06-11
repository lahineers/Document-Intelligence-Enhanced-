from uuid import UUID,uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field

class Insights(SQLModel,table=True):
    __tablename__="Insights"
    insight_id:UUID=Field(
        default_factory=uuid4,
        primary_key=True
    )
    doc_id:UUID=Field(
        foreign_key="Document.doc_id",
        index=True
    )
    session_id:UUID=Field(
        foreign_key="UploadSession.session_id",
        index=True
    )
    insight_text: str
    insight_type:str
    model_used:str
    scope:str
    created_at:datetime=Field(
        default_factory=datetime.utcnow
    )
    