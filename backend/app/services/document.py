import os
import shutil
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from pypdf import PdfReader

from app.repositories.document import DocumentRepository
from app.models import Document
from app.services.ai import AIService

class DocumentService:
    def __init__(self, db:AsyncSession):
        self.repo = DocumentRepository(db)
        self.ai_service = AIService()

    def _extract_text_from_pdf(self, file_path:str) -> str:
        try:
            reader = PdfReader(file_path)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            return extracted_text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    async def save_and_register_document(self, file: UploadFile, storage_dir: str) -> Document:
        clean_filename = file.filename.replace(" ", "_")
        file_path = os.path.join(storage_dir, clean_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pdf_text = self._extract_text_from_pdf(file_path=file_path)

        if not pdf_text:
            print("File does not contain any text!")
        else:
            print(f"Sucessfully extracted {len(pdf_text)} character from PDF.")

        if pdf_text:
            print("Sending text to Ollama Llama3...")
            ai_analysis = await self.ai_service.analyze_legal_text(pdf_text)
            print("\nWaiting on Response...")
            print(ai_analysis)
            print("------------------------------------------------------------")

        return await self.repo.create_document(filename=clean_filename, file_path=file_path)