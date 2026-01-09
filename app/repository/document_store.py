from typing import List, Union
from abc import ABC, abstractmethod
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

class DocumentStore(ABC):
    @abstractmethod
    def add_document(self, doc_id: int, text: str, vector: List[float]) -> None:
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], limit: int) -> List[str]:
        pass
    
    @abstractmethod
    def count(self) -> int:
        pass

class QdrantDocumentStore(DocumentStore):
    def __init__(self, url: str, collection_name: str, vector_size: int):
        self.client = QdrantClient(url)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self._initialize_collection()
    
    def _initialize_collection(self) -> None:
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )
    
    def add_document(self, doc_id: int, text: str, vector: List[float]) -> None:
        point = PointStruct(id=doc_id, vector=vector, payload={"text": text})
        self.client.upsert(collection_name=self.collection_name, points=[point])
    
    def search(self, query_vector: List[float], limit: int) -> List[str]:
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [hit.payload["text"] for hit in hits]
    
    def count(self) -> int:
        collection_info = self.client.get_collection(self.collection_name)
        return collection_info.points_count

class InMemoryDocumentStore(DocumentStore):
    def __init__(self):
        self.documents: List[str] = []
    
    def add_document(self, doc_id: int, text: str, vector: List[float]) -> None:
        self.documents.append(text)
    
    def search(self, query_vector: List[float], limit: int) -> List[str]:
        # DIKEMBALIKAN: Sesuai main.py asli, fallback in-memory hanya ambil data pertama
        if self.documents:
            return [self.documents[0]]
        return []
    
    def count(self) -> int:
        return len(self.documents)

def create_document_store(url: str, collection_name: str, vector_size: int) -> DocumentStore:
    try:
        # Tes koneksi singkat
        client = QdrantClient(url, timeout=1)
        client.get_collections()
        return QdrantDocumentStore(url, collection_name, vector_size)
    except Exception:
        return InMemoryDocumentStore()