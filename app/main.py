import time
import uuid  # DIUBAH: Tambahkan import uuid
from typing import List, Union # DIUBAH: Tambahkan Union untuk tipe data ID
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.services.embedding import EmbeddingService
from app.repository.document_store import create_document_store, DocumentStore
from app.services.rag_service import RAGWorkflow
from fastapi.responses import RedirectResponse

# Initialize FastAPI application
app = FastAPI(title=settings.app_title)


# Request/Response models
class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str


class QuestionResponse(BaseModel):
    """Response model for question answers."""
    question: str
    answer: str
    context_used: List[str]
    latency_sec: float


class DocumentRequest(BaseModel):
    """Request model for adding documents."""
    text: str


class DocumentResponse(BaseModel):
    """Response model for document addition."""
    id: Union[int, str] 
    status: str


class StatusResponse(BaseModel):
    """Response model for system status."""
    qdrant_ready: bool
    document_count: int
    workflow_ready: bool


# Dependency injection container
class ServiceContainer:
    """
    Container untuk mengelola dependensi layanan aplikasi
    
    Pola ini memungkinkan penyuntikan dependensi (dependency injection) dan pengujian
    yang lebih mudah, karena setiap layanan dapat diganti atau dipalsukan (mocking) 
    dengan mudah tanpa merusak logika utama
    
    Atribut:
        embedding_service: Layanan yang bertanggung jawab untuk menghasilkan vektor embedding
        document_store: Backend penyimpanan untuk dokumen (Qdrant atau In-Memory)
        rag_workflow: Orkesstrator yang mengatur alur kerja RAG (Retrieval-Augmented Generation)
        document_id_counter: Penghitung untuk menghasilkan ID dokumen unik secara berurutan
    """
    
    def __init__(self):
        """Initialize all services with proper dependency injection."""
        # Inisialisasi embedding service
        self.embedding_service = EmbeddingService(
            vector_size=settings.vector_size
        )
        
        # Inisialisasi document store
        self.document_store = create_document_store(
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection_name,
            vector_size=settings.vector_size
        )
        
        # Inisialisasi RAG workflow 
        self.rag_workflow = RAGWorkflow(
            embedding_service=self.embedding_service,
            document_store=self.document_store,
            search_limit=settings.search_limit
        )
        
        self.document_id_counter = 0
    
    def get_next_document_id(self) -> str:
        """
        Generate next document ID.
        
        Returns:
            A unique document identifier
        """
    
        return str(uuid.uuid4())
    
    def is_qdrant_ready(self) -> bool:
        """
        Check if Qdrant backend is being used.
        
        Returns:
            True if using Qdrant, False if using in-memory fallback
        """
        from app.repository.document_store import QdrantDocumentStore
        return isinstance(self.document_store, QdrantDocumentStore)



services = ServiceContainer()


# API Endpoints
@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> QuestionResponse:
    """
    Menjawab pertanyaan menggunakan workflow RAG
    
    Endpoint ini memproses pertanyaan pengguna melalui pipeline 
    Retrieval-Augmented Generation, lalu mengembalikan jawaban berdasarkan 
    dokumen-dokumen yang tersimpan di dalam database
    
    Argumen:
        request: Permintaan pertanyaan yang berisi teks pertanyaan dari pengguna
        
    Pengembalian:
        Response yang berisi jawaban, konteks yang digunakan, serta waktu pemrosesan
        
    Error:
        HTTPException: Jika terjadi kegagalan saat memproses pertanyaan
    """
    start_time = time.time()
    
    try:
        result = services.rag_workflow.process_question(request.question)
        
        return QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            context_used=result["context_used"],
            latency_sec=round(time.time() - start_time, 3)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@app.post("/add", response_model=DocumentResponse)
def add_document(request: DocumentRequest) -> DocumentResponse:
    """
    Menambahkan dokumen baru ke dalam basis knowledge base
    
    Endpoint ini menerima dokumen teks, menghasilkan embedding-nya,
    dan menyimpannya ke dalam document store untuk 
    keperluan pencarian di masa mendatang
    
    Argumen:
        request: Permintaan dokumen yang berisi teks untuk ditambahkan
        
    Pengembalian:
        Response yang berisi ID dokumen dan status penambahan
        
    Error:
        HTTPException: Jika terjadi kegagalan saat menambahkan dokumen
    """
    try:
        # Generate embedding for the document
        embedding = services.embedding_service.embed(request.text)
        
        # Get unique ID for this document
        doc_id = services.get_next_document_id()
        
        # Store the document
        services.document_store.add_document(
            doc_id=doc_id,
            text=request.text,
            vector=embedding
        )
        
        return DocumentResponse(
            id=doc_id,
            status="added"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add document: {str(e)}"
        )


@app.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    """
  
    Mendapatkan informasi status sistem
    
    Returns:
        Response status yang berisi informasi backend (apakah Qdrant siap) 
         dan jumlah dokumen yang tersimpan saat ini
    """
   
    return StatusResponse(
        qdrant_ready=services.is_qdrant_ready(),
        document_count=services.document_store.count(),
        workflow_ready=services.rag_workflow.chain is not None
    )


# Application startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    print(f" Starting {settings.app_title}")
    print(f" Vector size: {settings.vector_size}")
    print(f" Search limit: {settings.search_limit}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")