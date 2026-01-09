from typing import List, Dict, Any
from app.services.embedding import EmbeddingService
from app.repository.document_store import DocumentStore

class RAGWorkflow:
    def __init__(self, embedding_service: EmbeddingService, document_store: DocumentStore, search_limit: int = 2):
        self.embedding_service = embedding_service
        self.document_store = document_store
        self.search_limit = search_limit

    def process_question(self, question: str) -> Dict[str, Any]:
        query_vector = self.embedding_service.embed(question)
        contexts = self.document_store.search(query_vector, limit=self.search_limit)
        
        if contexts:
            answer = f"I found this: '{contexts[0][:100]}...'"
        else:
            answer = "Sorry, I don't know."
            
        return {
            "question": question,
            "answer": answer,
            "context_used": contexts
        }