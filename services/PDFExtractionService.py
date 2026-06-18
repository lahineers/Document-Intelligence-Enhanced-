from pathlib import Path
import pymupdf4llm
import fitz


class PDFExtractionService:

    @staticmethod
    def extract_markdown(pdf_path:str)->str:
        #extract markdown content from pdf
        #returns markdown content

        path=Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )
        
        markdown_content=(
            pymupdf4llm.to_markdown(str(path))
        )

        return markdown_content
    
    @staticmethod
    def extract_markdown_from_bytes(
        pdf_bytes: bytes
    ) -> str:

        doc = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        return pymupdf4llm.to_markdown(doc)