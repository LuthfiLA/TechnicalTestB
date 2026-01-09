import random
from typing import List


class EmbeddingService:
    """
    Layanan untuk menghasilkan fake embeddings untuk keperluan demonstrasi
    
    Layanan ini menggunakan pendekatan acak deterministik yang didasarkan pada teks input,
    sehingga memastikan teks yang sama akan selalu menghasilkan vektor embedding yang sama
    
    Atribut:
        vector_size: Dimensi atau panjang vektor yang dihasilkan
    """
    
    def __init__(self, vector_size: int = 128):
        """
        Inisialisasi embedding service.
        
        Args:
            vector_size: ukuran embedding vectors yang dihasilkan
        """
        self.vector_size = vector_size
    
    def embed(self, text: str) -> List[float]:
        """
       Menghasilkan embedding simulasi (fake embedding) yang deterministik untuk teks input.
    
    Embedding ini dihasilkan menggunakan pembuat angka acak
    yang diatur  berdasarkan hash dari teks input, guna menjamin 
    bahwa hasil tersebut dapat direproduksi 
    
    Argumen:
        text: Teks input yang akan dibuatkan embeddingnya
        
    Pengembalian:
        Daftar list of floats yang merepresentasikan vektor embedding
        
    Contoh:
        >>> service = EmbeddingService(vector_size=128)
        >>> embedding = service.embed("hello world")
        >>> len 128
        """
        # Seed based on input so it's deterministic
        random.seed(abs(hash(text)) % 10000)
        return [random.random() for _ in range(self.vector_size)]