from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Document(Base):
    """Модель документов СРО."""
    
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}', type='{self.document_type}')>"
    
    def to_dict(self) -> dict:
        """Преобразует объект в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "file_path": self.file_path,
            "document_type": self.document_type,
            "description": self.description,
            "content_hash": self.content_hash,
            "file_size": self.file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "version": self.version,
            "category": self.category,
            "tags": self.tags.split(",") if self.tags else [],
            "download_count": self.download_count
        }
    
    @property
    def file_extension(self) -> Optional[str]:
        """Возвращает расширение файла."""
        if self.file_path:
            return self.file_path.split(".")[-1].lower()
        return None
    
    @property
    def is_pdf(self) -> bool:
        """Проверяет, является ли файл PDF."""
        return self.file_extension == "pdf"
