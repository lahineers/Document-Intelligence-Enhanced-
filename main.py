from fastapi import FastAPI
from db import create_db_and_tables
from routers.user import router as user_router
from routers.upload_session import router as upload_session_router
from routers.document import router as document_router
from routers.document_chunk import router as document_chunk_router
from routers.chunk_embedding import router as chunk_embedding_router
from routers.session_summary import router as session_summary_router
from routers.query_session import router as query_session_router
from routers.messages import router as message_router
from routers.document_summary import router as document_summary_router
from routers.insights import router as insight_router
from routers.query import router as query_router
from routers.comparison import router as comparison_router

app=FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(user_router)
app.include_router(upload_session_router)
app.include_router(document_router)
app.include_router(document_chunk_router)
app.include_router(chunk_embedding_router)
app.include_router(session_summary_router)
app.include_router(query_session_router)
app.include_router(message_router)
app.include_router(document_summary_router)
app.include_router(insight_router)
app.include_router(query_router)
app.include_router(comparison_router)