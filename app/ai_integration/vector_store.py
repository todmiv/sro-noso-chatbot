from typing import List, Dict, Optional, Any
import numpy as np
import faiss
import pickle
import os
from pathlib import Path

from app.ai_integration.embeddings import EmbeddingService


class VectorStore:
    """Векторное хранилище для поиска похожих документов."""
    
    def __init__(self, dimension: int = 384, index_path: str = "data/vector_index"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.embedding_service = EmbeddingService()
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict[str, Any]] = []
        self.metadata: List[Dict[str, Any]] = []
        
        self._load_index()
    
    def _load_index(self) -> None:
        """Загружает индекс из файла."""
        index_file = self.index_path / "faiss_index.bin"
        docs_file = self.index_path / "documents.pkl"
        meta_file = self.index_path / "metadata.pkl"
        
        if index_file.exists() and docs_file.exists() and meta_file.exists():
            try:
                # Загружаем FAISS индекс
                self.index = faiss.read_index(str(index_file))
                
                # Загружаем документы
                with open(docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
                
                # Загружаем метаданные
                with open(meta_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                print(f"Loaded vector index with {len(self.documents)} documents")
                
            except Exception as e:
                print(f"Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Создает новый индекс."""
        # Используем IndexFlatIP для косинусного сходства
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents = []
        self.metadata = []
        print("Created new vector index")
    
    def _save_index(self) -> None:
        """Сохраняет индекс в файл."""
        try:
            index_file = self.index_path / "faiss_index.bin"
            docs_file = self.index_path / "documents.pkl"
            meta_file = self.index_path / "metadata.pkl"
            
            # Сохраняем FAISS индекс
            faiss.write_index(self.index, str(index_file))
            
            # Сохраняем документы
            with open(docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Сохраняем метаданные
            with open(meta_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            print(f"Saved vector index with {len(self.documents)} documents")
            
        except Exception as e:
            print(f"Error saving index: {e}")
    
    async def add_documents(
        self, 
        texts: List[str], 
        metadata: List[Dict[str, Any]] = None,
        source: str = None
    ) -> None:
        """Добавляет документы в векторное хранилище."""
        if not texts:
            return
        
        if metadata is None:
            metadata = [{}] * len(texts)
        
        if len(texts) != len(metadata):
            raise ValueError("Количество текстов и метаданных должно совпадать")
        
        # Генерируем эмбеддинги
        embeddings = await self.embedding_service.encode_batch(texts)
        
        # Нормализуем эмбеддинги для косинусного сходства
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Добавляем в индекс
        self.index.add(embeddings.astype('float32'))
        
        # Сохраняем документы и метаданные
        for i, (text, meta) in enumerate(zip(texts, metadata)):
            doc_meta = {
                'text': text,
                'source': source,
                'index': len(self.documents),
                **meta
            }
            
            self.documents.append(text)
            self.metadata.append(doc_meta)
        
        # Сохраняем индекс
        self._save_index()
        
        print(f"Added {len(texts)} documents to vector store")
    
    async def search(
        self, 
        query: str, 
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Ищет похожие документы."""
        if not self.index or len(self.documents) == 0:
            return []
        
        # Генерируем эмбеддинг для запроса
        query_embedding = await self.embedding_service.encode(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Поиск в индексе
        scores, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            min(top_k, len(self.documents))
        )
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score >= score_threshold:
                result = {
                    'content': self.documents[idx],
                    'score': float(score),
                    'metadata': self.metadata[idx]
                }
                results.append(result)
        
        return results
    
    async def add_document(self, text: str, metadata: Dict[str, Any] = None) -> None:
        """Добавляет один документ."""
        await self.add_documents([text], [metadata or {}])
    
    async def delete_documents_by_source(self, source: str) -> int:
        """Удаляет документы по источнику."""
        indices_to_remove = []
        
        for i, meta in enumerate(self.metadata):
            if meta.get('source') == source:
                indices_to_remove.append(i)
        
        if not indices_to_remove:
            return 0
        
        # Удаляем из списков (в обратном порядке для сохранения индексов)
        for i in sorted(indices_to_remove, reverse=True):
            del self.documents[i]
            del self.metadata[i]
        
        # Пересоздаем индекс
        await self._rebuild_index()
        
        return len(indices_to_remove)
    
    async def _rebuild_index(self) -> None:
        """Пересоздает индекс из существующих документов."""
        if not self.documents:
            self._create_new_index()
            self._save_index()
            return
        
        # Генерируем эмбеддинги для всех документов
        embeddings = await self.embedding_service.encode_batch(self.documents)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Создаем новый индекс
        self._create_new_index()
        self.index.add(embeddings.astype('float32'))
        
        # Обновляем индексы в метаданных
        for i, meta in enumerate(self.metadata):
            meta['index'] = i
        
        self._save_index()
        print(f"Rebuilt index with {len(self.documents)} documents")
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику векторного хранилища."""
        return {
            'total_documents': len(self.documents),
            'dimension': self.dimension,
            'index_size': self.index.ntotal if self.index else 0,
            'sources': list(set(meta.get('source', 'unknown') for meta in self.metadata))
        }
    
    async def update_embeddings(self) -> None:
        """Обновляет эмбеддинги для всех документов."""
        if self.documents:
            await self._rebuild_index()
            print("Updated embeddings for all documents")
    
    def clear(self) -> None:
        """Очищает векторное хранилище."""
        self._create_new_index()
        self._save_index()
        print("Cleared vector store")
