from typing import List, Dict, Optional
import os
from pathlib import Path

from app.ai_integration.document_processor import DocumentProcessor
from app.ai_integration.vector_store import VectorStore


class RAGSystem:
    """Система Retrieval-Augmented Generation для поиска в документах."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self._initialized = False
    
    async def initialize(self, documents_path: str = "documents/") -> None:
        """Инициализирует RAG систему, обрабатывая все документы."""
        if self._initialized:
            return
        
        docs_path = Path(documents_path)
        if not docs_path.exists():
            return
        
        # Обрабатываем все PDF файлы
        for pdf_file in docs_path.glob("**/*.pdf"):
            try:
                text = self.document_processor.extract_text(pdf_file)
                chunks = list(self.document_processor.split_into_chunks(text))
                
                # Добавляем в векторную базу
                await self.vector_store.add_documents(chunks, source=str(pdf_file))
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
        
        self._initialized = True
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """Ищет релевантные фрагменты документов."""
        if not self._initialized:
            await self.initialize()
        
        return await self.vector_store.search(query, top_k=top_k)
    
    async def add_document(self, file_path: str) -> None:
        """Добавляет новый документ в систему."""
        try:
            text = self.document_processor.extract_text(Path(file_path))
            chunks = list(self.document_processor.split_into_chunks(text))
            await self.vector_store.add_documents(chunks, source=file_path)
        except Exception as e:
            raise Exception(f"Failed to add document {file_path}: {e}")
