from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.document_chunk import DocumentChunk
from sqlalchemy.exc import IntegrityError
from schemas.document_chunk import(
    DocumentChunkCreate,
    DocumentChunkRead
)

router=APIRouter(
    prefix="/document_chunk",
    tags=["DocumentChunk"]
)

@router.post("", response_model=DocumentChunkRead)
def create_document_chunk(
    document_chunk_data: DocumentChunkCreate,
    session: SessionDep
):
    document_chunk = DocumentChunk(
        doc_id=document_chunk_data.doc_id,
        chunk_text=document_chunk_data.chunk_text,
        chunk_index=document_chunk_data.chunk_index,
        page_number=document_chunk_data.page_number,
        heading=document_chunk_data.heading
    )

    try:
        session.add(document_chunk)
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Failed to create chunk"
        )

    session.refresh(document_chunk)

    return document_chunk

@router.get("", response_model=list[DocumentChunkRead])
def read_document_chunk(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    document_chunk= (
        session.exec(
            select(DocumentChunk)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return document_chunk

@router.get("/{chunk_id}",
            response_model=DocumentChunkRead)
def read_document_chunk(
    chunk_id: UUID,
    session: SessionDep
):
    document_chunk = session.get(DocumentChunk, chunk_id)

    if not document_chunk:
        raise HTTPException(
            status_code=404,
            detail="Chunk not found"
        )

    return document_chunk


@router.delete("/{chunk_id}")
def delete_document_chunk(
    chunk_id: UUID,
    session: SessionDep
):
    document_chunk = session.get(
        DocumentChunk,
        chunk_id
    )

    if not document_chunk:
        raise HTTPException(
            status_code=404,
            detail="Chunk not found"
        )

    session.delete(document_chunk)

    session.commit()

    return {"ok": True}