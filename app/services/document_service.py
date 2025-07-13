from typing import List, Optional

from app.database.connection import get_async_session
from app.database.repositories.document_repository import DocumentRepository
from app.models.document import Document
from app.ai_integration.rag_system import RAGSystem


class DocumentService:
    """Сервис для работы с документами СРО."""
    
    def __init__(self):
        self.rag_system = RAGSystem()
    
    async def get_active_documents(self) -> List[Document]:
        """Возвращает список активных документов."""
        async with get_async_session() as session:
            doc_repo = DocumentRepository(session)
            return await doc_repo.get_active_documents()
    
    async def search_relevant_content(self, query: str) -> str:
        """Ищет релевантный контент в документах."""
        try:
            results = await self.rag_system.search(query, top_k=3)
            
            if not results:
                return "Релевантная информация не найдена."
            
            context = "\n\n".join([result["content"] for result in results])
            return context
            
        except Exception as e:
            # Логируем ошибку
            return "Ошибка поиска в документах."
    
    async def get_document_by_id(self, doc_id: int) -> Optional[Document]:
        """Получает документ по ID."""
        async with get_async_session() as session:
            doc_repo = DocumentRepository(session)
            return await doc_repo.get_by_id(doc_id)
