from fastapi import APIRouter, HTTPException,Query
from fastapi import UploadFile,File,Form
from pathlib import Path
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.document import Document
from sqlalchemy.exc import IntegrityError
from schemas.document import(
    DocumentCreate,
    DocumentRead,
    DocumentUpdate
)

from services.upload_document_service import UploadDocumentService

#testing:
from services.chunk_embedding_service import ChunkEmbeddingService
from services.llm_service import LLMService

from services.retrieval_service import RetrievalService

from services.ingestion_service import IngestionService
router=APIRouter(
    prefix="/document",
    tags=["Document"]
)


@router.post("", response_model=DocumentRead)
async def create_document(
    file: UploadFile = File(...),
    user_id: UUID = Form(...),
    session_id: UUID = Form(...),
    doc_type: str = Form(...),
    session: SessionDep = None
):
    saved_path = await (
        UploadDocumentService.save_file(file)
    )

    document = Document(
        user_id=user_id,
        session_id=session_id,
        doc_type=doc_type,
        file_name=file.filename,
        file_type=Path(file.filename).suffix.lower(),
        doc_path=saved_path
    )

    try:
        session.add(document)
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to add document"
        )

    session.refresh(document)

    try:

        IngestionService.ingest_document(
            document.doc_id,
            session
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document uploaded "
                f"but ingestion failed: {str(e)}"
            )
        )

    return document


##testing
@router.post(
    "/{doc_id}/embeddings"
)
def generate_embeddings(
    doc_id: UUID,
    session: SessionDep
):

    embeddings = (
        ChunkEmbeddingService
        .create_embeddings_for_document(
            doc_id,
            session
        )
    )

    return {
        "embeddings_created":
        len(embeddings)
    }

#testing
@router.get("/test-retrieval")
def test_retrieval(query:str, session:SessionDep):
    chunks=(RetrievalService.retrieve_chunks(query=query,session=session,top_k=5))
    return [
        {
            "chunk_id":str(chunk.chunk_id),
            "heading":chunk.heading,
            "preview":(chunk.chunk_text[:300])
        }
        for chunk in chunks
    ]


@router.get("/test-llm")
def test_llm():

    response = (
        LLMService.generate_response(
            "Explain revenue growth in one paragraph."
        )
    )

    return {
        "response": response
    }


@router.get("", response_model=list[DocumentRead])
def read_documents(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    documents = (
        session.exec(
            select(Document)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return documents

@router.get("/{doc_id}",
            response_model=DocumentRead)
def read_document(
    doc_id: UUID,
    session: SessionDep
):
    document = session.get(Document, doc_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document

@router.patch("/{doc_id}",
              response_model=DocumentRead)
def update_document(
    doc_id: UUID,
    document_update: DocumentUpdate,
    session: SessionDep
):
    document = session.get(Document, doc_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    update_data = document_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(document, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to update document"
        )

    session.refresh(document)

    return document

@router.delete("/{doc_id}")
def delete_document(
    doc_id: UUID,
    session: SessionDep
):
    document = session.get(
        Document,
        doc_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    session.delete(document)

    session.commit()

    return {"ok": True}

