from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from core.settings import settings

class UploadDocumentService:

    @staticmethod
    async def save_file(
        file:UploadFile
    ) ->str:
    
    #save uploaded file locally and return metadata

        upload_dir=Path(settings.upload_dir)
        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

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

        saved_path=(
            upload_dir
            / generated_filename
        )
        content=await file.read()

        if not content:
            raise ValueError(
                "Uploaded file is empty"
            )
        
        with open(
            saved_path,
            "wb"
        ) as f:
            f.write(content)

        return str(saved_path)