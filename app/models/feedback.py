from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Feedback(Base):
    """Модель отзывов пользователей."""
    
    __tablename__ = "feedback"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'response', 'general', 'bug'
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    admin_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="feedback")
    message: Mapped[Optional["Message"]] = relationship("Message")
    
    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, user_id={self.user_id}, rating={self.rating}, type='{self.feedback_type}')>"
    
    def to_dict(self) -> dict:
        """Преобразует объект в словарь."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message_id": self.message_id,
            "rating": self.rating,
            "comment": self.comment,
            "feedback_type": self.feedback_type,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_processed": self.is_processed,
            "admin_response": self.admin_response,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "processed_by": self.processed_by
        }
    
    @property
    def is_positive(self) -> bool:
        """Проверяет, является ли отзыв положительным."""
        return self.rating >= 4
    
    @property
    def is_negative(self) -> bool:
        """Проверяет, является ли отзыв отрицательным."""
        return self.rating <= 2
