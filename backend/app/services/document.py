import os
import shutil
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import httpx

from app.core.config import settings
from app.repositories.document import DocumentRepository
from app.models import Document
from app.services.ai import AIService
from app.services.vector import VectorService

class DocumentService:
    def __init__(self, db:AsyncSession):
        self.repo = DocumentRepository(db)
        self.ai_service = AIService()
        self.vector_service = VectorService()

        # Setup text splitter (split based on paragraph or sentence naturally)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200
        )

    async def get_document_list(self):
        try:
            return await self.repo.get_document_list()
        except Exception as e:
            raise Exception(f"Failed to retrieve documents list")
        

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
        

    # AI-Integration auto response (prompt)
    async def analyze_document(self, document_id) -> Document:
        document = await self.repo.get_document(document_id)
        file_path = document.file_path

        pdf_text = self._extract_text_from_pdf(file_path=file_path)

        if not pdf_text:
            print("File does not contain any text!")
        else:
            print(f"Sucessfully extracted {len(pdf_text)} character from PDF.")

        if pdf_text:
            print("Sending text to Ollama Llama3...")
            ai_analysis = await self.ai_service.analyze_legal_text(pdf_text)
            print("\nWaiting on Response...")

        return {"response": ai_analysis}
    
    async def save_document(self, file: UploadFile, storage_dir: str) -> Document:
        clean_filename = file.filename.replace(" ", "_")
        file_path = os.path.join(storage_dir, clean_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return await self.repo.create_document(filename=clean_filename, file_path=file_path)
        
    async def vectorize_document_rag(self, document_id: int, file_path: str):
        # Extract Text
        raw_text = self._extract_text_from_pdf(file_path)

        if not raw_text:
            raise Exception("File does not contain any text!")
        
        # Chunking Process
        chunks = self.text_splitter.split_text(raw_text)

        # Save chunks into Local Vector Database
        self.vector_service.store_chunks(document_id=document_id, chunks=chunks)

        # Temp: Testing purpose
        # sample_context = "\n----\n".join(chunks[:3])
        # print(sample_context)

        await self.repo.update_vectorized_status(document_id=document_id)


    async def query_document_rag(self, document_id: int, question: str):

        try:
            document = await self.repo.get_document(document_id=document_id)

            print(document)

            if document.status == "COMPLETED" and document.vectorized == 1: 
                pass

            else:
                print("Vectorizing")
                await self.vectorize_document_rag(document_id=document.id, file_path=document.file_path)

        except Exception as e:
            print(e)
            raise
        
        # Take chunks of relevant text vector from chromadb based on user question
        relevant_chunks = self.vector_service.query_relevant_chunks(
            document_id=document.id,
            query=question,
            top_k=3
        )

        if not relevant_chunks:
            return {
                "answer": "No relevant information in this document that related to your question",
                "source_chunks": []
            }
        
        # Prompt Engineering (insert text chunk to improve AI)
        context_text = "\n\n---\n\n".join(relevant_chunks)

        # Strict Prompt to reduce AI Hallucination
        system_instruction = (
            "You are DraftLens AI, a precise and objective legal assistant. "
            "Your task is to answer the user's questions ONLY based on the reference documents provided below.\n"
            "Strict rules:\n"
            "1. If the answer is not contained in the reference documents, honestly state that you do not know.\n"
            "2. Do not fabricate information or use external knowledge beyond the provided documents.\n"
            "3. Provide answers that are well-structured and easy to understand.\n\n"
            f"REFERENCE DOCUMENTS:\n{context_text}"
        )

        # AI Endpoint
        ollama_url = settings.OLLAMA_URL
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": f"{system_instruction}\n\nPertanyaan Pengguna: {question}\n Jawaban:",
            "stream": False

        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(ollama_url, json=payload)
                response.raise_for_status()
                result = response.json()

                ai_answer = result.get("response", "").strip()

                return {
                    "answer": ai_answer,
                    # "source_chunks": relevant_chunks
                }

        except Exception as e:
            raise Exception(f"Internal Server Error on RAG: {str(e)}")
        
    async def check_document(self, document_id: int):
        return await self.repo.get_document(document_id=document_id)