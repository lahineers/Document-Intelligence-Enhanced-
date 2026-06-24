from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep 
from uuid import UUID
from models.document_summary import DocumentSummary
from schemas.document_summary import(
    DocumentSummaryCreate,
    DocumentSummaryRead
)

from services.document_summary_service import DocumentSummaryService

router=APIRouter(
    prefix="/document_summary",
    tags=["DocumentSummary"]
)

@router.post("/{doc_id}/generate")
def generate_summary(
    doc_id: UUID,
    session: SessionDep
):

    return (
        DocumentSummaryService
        .generate_summary(
            doc_id,
            session
        )
    )

@router.get("/document/{doc_id}")
def get_summary_by_document(
    doc_id: UUID,
    session: SessionDep
):
    
    statement = (
        select(DocumentSummary)
        .where(
            DocumentSummary.doc_id == doc_id
        )
    )

    summary = (
        session.exec(statement)
        .first()
    )

    if not summary:

        raise HTTPException(
            status_code=404,
            detail="Summary not found"
        )

    return summary


@router.get("/{document_summary_id}",
            response_model=DocumentSummaryRead)
def read_document_summary(
    document_summary_id: UUID,
    session: SessionDep
):
    document_summary = session.get(DocumentSummary, document_summary_id)

    if not document_summary:
        raise HTTPException(
            status_code=404,
            detail="Document Summary not found"
        )

    return document_summary


@router.delete("/{document_summary_id}")
def delete_document_summary(
    document_summary_id: UUID,
    session: SessionDep
):
    document_summary = session.get(
        DocumentSummary,
        document_summary_id
    )

    if not document_summary:
        raise HTTPException(
            status_code=404,
            detail="Document Summary not found"
        )

    session.delete(document_summary)

    session.commit()

    return {"ok": True}