from typing import List, Dict, Optional
import os
from pathlib import Path

from app.ai_integration.document_processor import DocumentProcessor
from app.ai_integration.vector_store import VectorStore
from app.ai_integration.embeddings import EmbeddingService


class RAGSystem:
    """Система Retrieval-Augmented Generation для поиска в документах."""
    
    def __init__(self, embedding_service=None, vector_store=None):
        
        self.document_processor = DocumentProcessor()
        self.vector_store = vector_store or VectorStore(
            dimension=embedding_service.get_embedding_dimension() if embedding_service else 384
        )
        self.embedding_service = embedding_service
        self._initialized = False
    
    async def initialize(self, documents_path: str = "data/documents/") -> None:
        """Инициализирует RAG систему, обрабатывая все документы."""
        try:
            print(f"[INFO][RAGSystem] Starting recursive search in: {documents_path}")
            if self._initialized:
                print("[DEBUG][RAGSystem] Already initialized")
                return
            
            docs_path = Path(documents_path)
            if not docs_path.exists():
                print(f"[ERROR][RAGSystem] Documents path not found: {docs_path}")
                raise FileNotFoundError(f"Documents directory not found: {docs_path}")

            print("[INFO] Document directory structure:")
            for path in docs_path.glob("**/*"):
                if path.is_file():
                    print(f" - {path.relative_to(docs_path)}")

        except Exception as e:
            print(f"[ERROR][RAGSystem] Initialize failed: {str(e)}")
            traceback.print_exc()
            raise
        
        # Обрабатываем все поддерживаемые форматы
        supported_formats = ["*.pdf", "*.doc", "*.docx", "*.txt"]
        for ext in supported_formats:
            for doc_file in docs_path.glob(f"**/{ext}"):
                try:
                    print(f"[DEBUG] Processing {doc_file.relative_to(docs_path)}")
                    text = self.document_processor.extract_text(doc_file)
                    chunks = list(self.document_processor.split_into_chunks(text))
                    
                    # Добавляем в векторную базу
                    await self.vector_store.add_documents(chunks, source=str(doc_file))
                    
                except Exception as e:
                    print(f"Ошибка обработки {doc_file}: {e}")
                    if 'textract' in str(e) or 'additional dependencies' in str(e):
                        print("Рекомендация: Для обработки .doc файлов установите пакет textract командой: pip install textract. "
                              "Также могут потребоваться системные зависимости, см. https://textract.readthedocs.io/en/stable/installation.html")
        
        self._initialized = True
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """Ищет релевантные фрагменты документов."""
        try:
            if not self._initialized:
                await self.initialize()
            
            print(f"[DEBUG][RAGSystem] Searching for: {query}")
            results = await self.vector_store.search(query, top_k=top_k)
            print(f"[DEBUG][RAGSystem] Found {len(results)} results")
            return results
            
        except Exception as e:
            import traceback
            print(f"[ERROR][RAGSystem] Search failed: {str(e)}")
            traceback.print_exc()
            raise
    
    async def add_document(self, file_path: str) -> None:
        """Добавляет новый документ в систему."""
        try:
            text = self.document_processor.extract_text(Path(file_path))
            chunks = list(self.document_processor.split_into_chunks(text))
            await self.vector_store.add_documents(chunks, source=file_path)
        except Exception as e:
            raise Exception(f"Failed to add document {file_path}: {e}")
    
    # В app/ai_integration/rag_system.py добавить метод:
async def generate_response(
    self, 
    question: str, 
    context: str = None, 
    user_id: int = None
) -> str:
    """Генерирует ответ используя RAG + DeepSeek."""
    from app.ai_integration.deepseek_client import DeepSeekClient
    
    # Получаем контекст из документов если не передан
    if not context:
        search_results = await self.search(question, top_k=3)
        context = "\n\n".join([result.get("content", "") for result in search_results])
    
    # Создаем клиента DeepSeek
    deepseek_client = DeepSeekClient()
    
    try:
        response = await deepseek_client.generate_response(
            user_question=question,
            context=context
        )
        return response
    finally:
        await deepseek_client.close()

# Глобальный экземпляр RAG системы
from app.services.global_services import services
rag_system_instance = RAGSystem(
    embedding_service=services.embedding_service,
    vector_store=services.vector_store
)
