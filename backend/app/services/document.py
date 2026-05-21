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
        
    
    # RAG Pipeline
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
        sample_context = "\n----\n".join(chunks[:3])
        print(sample_context)

        await self.repo.update_vectorized_status(document_id=document_id)


    async def query_document_rag(self, document_id: int, question: str):

        try:
            document = await self.repo.get_document(document_id=document_id)

            print(document)

            if document.vectorized == 0:
                print("Vectorizing")
                await self.vectorize_document_rag(document_id=document.id, file_path=document.file_path)
        except Exception as e:
            raise Exception("document id doesnt exist")
        
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
            "Anda adalah DraftLens AI, seorang asisten ahli hukum yang presisi dan objektif. "
            "Tugas Anda adalah menjawab pertanyaan pengguna HANYA berdasarkan dokumen referensi yang disediakan di bawah ini.\n"
            "Aturan ketat:\n"
            "1. Jika jawabannya tidak ada di dalam dokumen referensi, katakan secara jujur bahwa Anda tidak mengetahuinya.\n"
            "2. Jangan mengarang informasi atau menggunakan pengetahuan luar di luar dokumen yang diberikan.\n"
            "3. Berikan jawaban yang terstruktur dan mudah dipahami.\n\n"
            f"DOKUMEN REFERENSI:\n{context_text}"
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
            
# ─── PERBAIKI BAGIAN INI ───
        except httpx.HTTPStatusError as e:
            # Menangkap jika Ollama merespon tapi status kodenya error (misal 404 atau 500)
            raise Exception(f"Ollama mengembalikan status error: {e.response.status_code} - {e.response.text}")
            
        except httpx.RequestError as e:
            # Menangkap jika gagal konek ke Ollama (misal Ollama belum dinyalakan)
            raise Exception(f"Gagal terhubung ke Ollama lokal di {e.request.url}. Apakah Ollama sudah dinyalakan?")
            
        except Exception as e:
            # Menangkap error umum lainnya
            raise Exception(f"Terjadi kesalahan internal pada RAG: {str(e)}")

        except httpx.HTTPError() as e :
            raise Exception(f"Gagal berkomunikasi dengan Ollama lokal; {str(e)}")
        