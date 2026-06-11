from datetime import datetime
from sqlmodel import SQLModel
from uuid import UUID
from typing import Optional

class InsightsCreate(SQLModel):
    doc_id: UUID
    session_id: UUID
    model_used:str
    scope:str

class InsightRead(SQLModel):
    insight_id:UUID
    doc_id:UUID
    session_id:UUID
    insight_text:str
    insight_type:str
    model_used:str
    scope:str
    created_at:datetime

class InsightUpdate(SQLModel):
    insight_text:Optional[str]=None
    scope:Optional[str]=None