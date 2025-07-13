from typing import List, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
import asyncio
from functools import lru_cache


class EmbeddingService:
    """Сервис для генерации эмбеддингов текста."""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self) -> None:
        """Загружает модель для создания эмбеддингов."""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"Loaded embedding model: {self.model_name} on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback к базовой модели
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
            print("Loaded fallback model: all-MiniLM-L6-v2")
    
    async def encode(self, text: str) -> np.ndarray:
        """Создает эмбеддинг для одного текста."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        # Выполняем в отдельном потоке для неблокирующего выполнения
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, 
            lambda: self.model.encode(text, convert_to_numpy=True)
        )
        
        return embedding
    
    async def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Создает эмбеддинги для списка текстов."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        if not texts:
            return np.array([])
        
        # Выполняем в отдельном потоке для неблокирующего выполнения
        loop = asyncio.get_event_loop()
        
        # Обрабатываем батчами для экономии памяти
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
            )
            embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings)
    
    @lru_cache(maxsize=1000)
    def encode_cached(self, text: str) -> np.ndarray:
        """Создает эмбеддинг с кешированием для часто используемых текстов."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        return self.model.encode(text, convert_to_numpy=True)
    
    async def similarity(self, text1: str, text2: str) -> float:
        """Вычисляет косинусное сходство между двумя текстами."""
        embedding1 = await self.encode(text1)
        embedding2 = await self.encode(text2)
        
        # Косинусное сходство
        cosine_sim = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        return float(cosine_sim)
    
    async def find_most_similar(self, query: str, texts: List[str], top_k: int = 5) -> List[dict]:
        """Находит наиболее похожие тексты."""
        if not texts:
            return []
        
        query_embedding = await self.encode(query)
        text_embeddings = await self.encode_batch(texts)
        
        # Вычисляем косинусное сходство
        similarities = np.dot(text_embeddings, query_embedding) / (
            np.linalg.norm(text_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Сортируем по убыванию сходства
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'text': texts[idx],
                'similarity': float(similarities[idx]),
                'index': int(idx)
            })
        
        return results
    
    def get_embedding_dimension(self) -> int:
        """Возвращает размерность эмбеддингов."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> dict:
        """Возвращает информацию о модели."""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'dimension': self.get_embedding_dimension() if self.model else None,
            'max_seq_length': self.model.max_seq_length if self.model else None
        }
    
    async def cluster_texts(self, texts: List[str], n_clusters: int = 5) -> List[List[int]]:
        """Кластеризует тексты по эмбеддингам."""
        if len(texts) < n_clusters:
            return [[i] for i in range(len(texts))]
        
        embeddings = await self.encode_batch(texts)
        
        # Используем K-means для кластеризации
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # Группируем индексы по кластерам
        clusters = [[] for _ in range(n_clusters)]
        for idx, label in enumerate(cluster_labels):
            clusters[label].append(idx)
        
        return clusters
    
    async def semantic_search(
        self, 
        query: str, 
        documents: List[str], 
        threshold: float = 0.5,
        top_k: int = 10
    ) -> List[dict]:
        """Семантический поиск в документах."""
        if not documents:
            return []
        
        # Создаем эмбеддинги
        query_embedding = await self.encode(query)
        doc_embeddings = await self.encode_batch(documents)
        
        # Вычисляем сходства
        similarities = np.dot(doc_embeddings, query_embedding) / (
            np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Фильтруем по порогу и сортируем
        results = []
        for idx, similarity in enumerate(similarities):
            if similarity >= threshold:
                results.append({
                    'document': documents[idx],
                    'similarity': float(similarity),
                    'index': idx
                })
        
        # Сортируем по убыванию сходства
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:top_k]
    
    def clear_cache(self) -> None:
        """Очищает кеш эмбеддингов."""
        self.encode_cached.cache_clear()
        print("Cleared embedding cache")
