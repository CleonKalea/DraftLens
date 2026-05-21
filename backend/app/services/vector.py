import os
import chromadb

from typing import List

class VectorService:
    def __init__(self):
        # Path Chroma DB
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chroma_db"))

        # Init Chroma DB Client (Persistent = save on hard disk)
        self.client = chromadb.PersistentClient(path=self.db_path)

    def get_or_create_collection(self, document_id: int):
        # get or create a special vector collection per document
        return self.client.get_or_create_collection(name=f"doc_{document_id}")
    
    def store_chunks(self, document_id: int, chunks: List[str]):
        # Save text chunk to Vector DB
        collection = self.get_or_create_collection(document_id=document_id)

        # Generate unique ID for every chunk
        ids = [f"chunk{i}" for i in range(len(chunks))]

        # Default embedding (all-MiniLM-L6-v2)
        collection.add(
            documents=chunks,
            ids=ids
        )

    def query_relevant_chunks(self, document_id: int, query: str, top_k: int = 3) -> List[str]:
        # Find most relevant chunk with user question
        collection = self.get_or_create_collection(document_id)
        
        results = collection.query(
            query_texts=query,
            n_results=top_k
        )

        return results['documents'][0] if results['documents'] else []

