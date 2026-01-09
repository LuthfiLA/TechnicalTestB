
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Pengaturan aplikasi yang dimuat dari variabel lingkungan (.env).
    
    Atribut:
        qdrant_url: URL untuk koneksi ke database vektor Qdrant.
        qdrant_collection_name: Nama koleksi untuk menyimpan vektor.
        vector_size: Dimensi dari vektor embedding (default: 128).
        app_title: Judul untuk aplikasi FastAPI.
        search_limit: Jumlah maksimal hasil pencarian yang dikembalikan.
    """
    
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "demo_collection"
    vector_size: int = 128
    app_title: str = "Tugas"
    search_limit: int = 2
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()