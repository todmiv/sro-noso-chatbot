from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Session(Base):
    """Модель сессий пользователей."""
    
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    session_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, session_id='{self.session_id}', active={self.is_active})>"
    
    def to_dict(self) -> dict:
        """Преобразует объект в словарь."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "session_end": self.session_end.isoformat() if self.session_end else None,
            "is_active": self.is_active,
            "context": self.context,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address
        }
    
    @property
    def duration(self) -> Optional[int]:
        """Возвращает продолжительность сессии в секундах."""
        if self.session_end:
            return int((self.session_end - self.created_at).total_seconds())
        elif self.is_active:
            return int((datetime.utcnow() - self.created_at).total_seconds())
        return None
    
    def close(self) -> None:
        """Закрывает сессию."""
        self.is_active = False
        self.session_end = datetime.utcnow()
