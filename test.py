import fitz
import pymupdf4llm

from services.minio_service import minio_service

pdf_bytes = minio_service.download_bytes(
    "raw/8394f197-76ec-43b8-a6bc-a9a620541e7d.pdf"
)

doc = fitz.open(
    stream=pdf_bytes,
    filetype="pdf"
)

markdown = pymupdf4llm.to_markdown(doc)

print(len(markdown))