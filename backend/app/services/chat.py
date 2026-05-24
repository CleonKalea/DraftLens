from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat import ChatRepository
from app.services.document import DocumentService
from app.services.ai import AIService
from app.services.vector import VectorService
from app.core.config import settings
import httpx
from typing import Optional

class ChatServices():
    def __init__(self, db: AsyncSession):
        self.repo = ChatRepository(db)
        self.document_service = DocumentService(db)
        self.ai_service = AIService()
        self.vector_service = VectorService()

    async def create_chat_session(self, document_id: int, title: str):
        try:
            doc_check = await self.document_service.check_document(document_id=document_id)
            print(f"DOC CHECK: {doc_check}")
        
        except Exception as e:
            raise Exception(f"No document found with id: {document_id}| {str(e)}")
        
        return await self.repo.create_new_session(document_id=document_id, title=title)
    
    async def get_chat_sessions(self, document_id: Optional[int]):
        try: 
            return await self.repo.get_chat_sessions(document_id=document_id)
        
        except Exception as e:
            raise Exception(f"Failed to retrieve chat sessions: {str(e)}")
        
    async def get_session_messages(self, session_id: int):
        try:
            return await self.repo.get_session_messages(session_id=session_id)
        except Exception as e:
            raise Exception(f"Failed to retrieve session messages: {str(e)}")
        
    async def query_response_stream(self, session_id: int, user_question: str):
        try:
            # 1. Simpan pertanyaan user
            await self.repo.save_message(session_id=session_id, role="user", content=user_question)
            past_messages = await self.repo.get_session_messages(session_id)

            history_context = ""
            for msg in past_messages[-7:-1]:
                history_context += f"{msg.role.capitalize()}: {msg.content}\n"

            # 2. Ambil context dokumen
            session_info = await self.repo.get_session_by_id(session_id)
            document_id = session_info.document_id

            document_context = await self.vector_service.query_relevant_chunks(
                document_id=document_id,
                query=user_question,
                top_k=3
            )

            # 3. Susun Prompt RAG
            system_prompt = (
                "Kamu adalah DraftLens AI, asisten peninjau dokumen hukum yang presisi.\n"
                "Gunakan riwayat obrolan dan dokumen referensi di bawah ini untuk menjawab pertanyaan user.\n\n"
                f"--- RIWAYAT OBROLAN PREVIOUS ---\n{history_context if history_context else 'Tidak ada obrolan sebelumnya.'}\n"
                f"--- DOKUMEN REFERENSI ASLI ---\n{document_context}\n\n"
                f"Pertanyaan User Saat Ini: {user_question}\n"
                "Jawaban Analisis Hukum:"
            )

            full_ai_response = ""

            # 4. Payload Ollama dengan AKTIFKAN STREAM
            ollama_url = settings.OLLAMA_URL
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": system_prompt, # ➕ Tambah koma
                "stream": True           # 🔄 Diubah jadi True untuk streaming
            }
            
            try:
                # 🔌 Menggunakan client.stream alih-alih client.post biasa
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream("POST", ollama_url, json=payload) as response:
                        response.raise_for_status()
                        
                        # Membaca respons baris demi baris dari Ollama
                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            
                            # Ollama mengembalikan response berupa baris-baris JSON terpisah
                            import json
                            data = json.loads(line)
                            chunk_text = data.get("response", "")
                            
                            full_ai_response += chunk_text
                            
                            # Kirim potongan kata langsung ke browser (Format SSE)
                            yield f"data: {chunk_text}\n\n"
                            
                            # Hentikan jika Ollama sudah mengirim sinyal selesai
                            if data.get("done", False):
                                break

                # 5. KUNCI DATA: Setelah stream sukses berakhir, simpan jawaban utuh AI ke Postgres
                await self.repo.save_message(
                    session_id=session_id, 
                    role="assistant", 
                    content=full_ai_response.strip()
                )

            except Exception as e:
                yield f"data: [ERROR] Gagal streaming dari Ollama: {str(e)}\n\n"
                raise Exception(f"Internal Server Error on RAG Stream: {str(e)}")

        except Exception as e:
            raise e

        except Exception as e:
            raise Exception(f"Failed to response messages: {str(e)}")
    






