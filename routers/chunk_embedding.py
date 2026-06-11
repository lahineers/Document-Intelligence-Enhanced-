from fastapi import APIRouter, HTTPException,Query
from typing import Annotated
from sqlmodel import select
from db import SessionDep
from uuid import UUID
from models.chunk_embedding import ChunkEmbedding
from sqlalchemy.exc import IntegrityError
from schemas.chunk_embedding import(
    ChunkEmbeddingCreate,
    ChunkEmbeddingRead
)

router=APIRouter(
    prefix="/chunk_embedding",
    tags=["ChunkEmbedding"]
)

#@router.post("", response_model=ChunkEmbeddingRead)
#def create_chunk_embedding(

#chunk_embedding_data: ChunkEmbeddingCreate,
 #   session: SessionDep
#):
   # chunk_embedding = ChunkEmbedding(
   #     chunk_id=chunk_embedding_data.chunk_id,
  #      model_name=chunk_embedding_data.model_name,      
 #       )
#
  #  try:
    #    session.add(chunk_embedding)
    #    session.commit()

    #except IntegrityError:
   #     session.rollback()

  #      raise HTTPException(
 #           status_code=400,
 #           detail="Failed to create chunk"
 #       )

 #   session.refresh(chunk_embedding)

#    return chunk_embedding

@router.get("", response_model=list[ChunkEmbeddingRead])
def read_chunk_embeddings(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    chunk_embedding= (
        session.exec(
            select(ChunkEmbedding)
            .offset(offset)
            .limit(limit)
        )
        .all()
    )

    return chunk_embedding

@router.get("/{embedding_id}",
            response_model=ChunkEmbeddingRead)
def read_chunk_embedding(
    embedding_id: UUID,
    session: SessionDep
):
    chunk_embedding = session.get(ChunkEmbedding, embedding_id)

    if not chunk_embedding:
        raise HTTPException(
            status_code=404,
            detail="Embedding not found"
        )

    return chunk_embedding


@router.delete("/{embedding_id}")
def delete_chunk_embedding(
    embedding_id: UUID,
    session: SessionDep
):
    chunk_embedding = session.get(
        ChunkEmbedding,
        embedding_id
    )

    if not chunk_embedding:
        raise HTTPException(
            status_code=404,
            detail="Embedding not found"
        )

    session.delete(chunk_embedding)

    session.commit()

    return {"ok": True}