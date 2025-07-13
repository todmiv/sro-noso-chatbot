from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    """Репозиторий для работы с документами."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, document: Document) -> Document:
        """Сохраняет документ."""
        self._session.add(document)
        await self._session.commit()
        await self._session.refresh(document)
        return document
    
    async def get_by_id(self, document_id: int) -> Optional[Document]:
        """Получает документ по ID."""
        stmt = select(Document).where(Document.id == document_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_title(self, title: str) -> Optional[Document]:
        """Получает документ по названию."""
        stmt = select(Document).where(Document.title == title)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_documents(self, limit: int = 100) -> List[Document]:
        """Получает активные документы."""
        stmt = (
            select(Document)
            .where(Document.is_active == True)
            .order_by(desc(Document.last_updated))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_public_documents(self, limit: int = 100) -> List[Document]:
        """Получает публичные документы."""
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.is_active == True,
                    Document.is_public == True
                )
            )
            .order_by(desc(Document.last_updated))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_documents_by_type(self, document_type: str, limit: int = 50) -> List[Document]:
        """Получает документы по типу."""
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.document_type == document_type,
                    Document.is_active == True
                )
            )
            .order_by(desc(Document.last_updated))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_documents_by_category(self, category: str, limit: int = 50) -> List[Document]:
        """Получает документы по категории."""
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.category == category,
                    Document.is_active == True
                )
            )
            .order_by(desc(Document.last_updated))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_documents(self, query: str, limit: int = 50) -> List[Document]:
        """Поиск документов по названию и описанию."""
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.is_active == True,
                    or_(
                        Document.title.ilike(f"%{query}%"),
                        Document.description.ilike(f"%{query}%"),
                        Document.tags.ilike(f"%{query}%")
                    )
                )
            )
            .order_by(desc(Document.last_updated))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_document_types(self) -> List[str]:
        """Получает список типов документов."""
        stmt = (
            select(Document.document_type)
            .where(Document.is_active == True)
            .distinct()
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]
    
    async def get_document_categories(self) -> List[str]:
        """Получает список категорий документов."""
        stmt = (
            select(Document.category)
            .where(
                and_(
                    Document.is_active == True,
                    Document.category.is_not(None)
                )
            )
            .distinct()
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]
    
    async def increment_download_count(self, document_id: int) -> None:
        """Увеличивает счетчик скачиваний."""
        document = await self.get_by_id(document_id)
        if document:
            document.download_count += 1
            await self._session.commit()
    
    async def get_popular_documents(self, limit: int = 10) -> List[Document]:
        """Получает популярные документы."""
        stmt = (
            select(Document)
            .where(Document.is_active == True)
            .order_by(desc(Document.download_count))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_documents(self, limit: int = 10) -> List[Document]:
        """Получает недавно добавленные документы."""
        stmt = (
            select(Document)
            .where(Document.is_active == True)
            .order_by(desc(Document.upload_date))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_documents(self) -> int:
        """Подсчитывает общее количество активных документов."""
        stmt = select(func.count(Document.id)).where(Document.is_active == True)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def deactivate_document(self, document_id: int) -> bool:
        """Деактивирует документ."""
        document = await self.get_by_id(document_id)
        if document:
            document.is_active = False
            await self._session.commit()
            return True
        return False
    
    async def update_document_hash(self, document_id: int, content_hash: str) -> bool:
        """Обновляет хэш содержимого документа."""
        document = await self.get_by_id(document_id)
        if document:
            document.content_hash = content_hash
            document.last_updated = datetime.utcnow()
            await self._session.commit()
            return True
        return False
