"""Модуль для хранения глобальных сервисов приложения."""
from typing import Optional
from app.ai_integration.embeddings import EmbeddingService
from app.ai_integration.vector_store import VectorStore
from app.ai_integration.rag_system import RAGSystem

class GlobalServices:
    """Класс для хранения и управления глобальными сервисами."""
    
    _instance = None
    _embedding_service: Optional[EmbeddingService] = None
    _vector_store: Optional[VectorStore] = None
    _rag_system: Optional[RAGSystem] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def embedding_service(self) -> EmbeddingService:
        """Глобальный сервис эмбеддингов."""
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    @property
    def vector_store(self) -> VectorStore:
        """Глобальное хранилище векторов."""
        if self._vector_store is None:
            dimension = self.embedding_service.get_embedding_dimension()
            self._vector_store = VectorStore(self.embedding_service, dimension=dimension)
        return self._vector_store

    @property
    def rag_system(self) -> RAGSystem:
        """Глобальная RAG система."""
        if self._rag_system is None:
            self._rag_system = RAGSystem(
                embedding_service=self.embedding_service,
                vector_store=self.vector_store
            )
        return self._rag_system

# Глобальный экземпляр сервисов
services = GlobalServices()
