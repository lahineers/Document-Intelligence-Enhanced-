from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from core.settings import settings

from services.minio_service import minio_service

class UploadDocumentService:

    @staticmethod
    async def save_file(
        file:UploadFile
    ) ->str:
    
    #save uploaded file locally and return metadata



        if not file.filename:
            raise ValueError(
                "Filename is required"
            )
        
        extension=(
            Path(file.filename).suffix.lower()
        )

        allowed_extensions={
            ".pdf",
            ".xlsx"
        }

        if extension not in allowed_extensions:
            raise ValueError(
                f"Unsupported file type:{extension}"
            )
        
        generated_filename=(
            f"{uuid4()}{extension}"
        )

        
        content=await file.read()

        object_key = (f"raw/{generated_filename}")

        minio_service.upload_bytes(
            data=content,
            object_key=object_key,
            content_type=file.content_type or "application/octet-stream"
        )

        if not content:
            raise ValueError(
                "Uploaded file is empty"
            )
        
        return object_key
        