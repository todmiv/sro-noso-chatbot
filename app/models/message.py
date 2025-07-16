from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Message(Base):
    """Модель сообщений в диалоге."""
    
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    bot_response: Mapped[str] = mapped_column(Text, nullable=False)
    context_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Связи
    session: Mapped["Session"] = relationship("Session", back_populates="messages")
    user: Mapped["User"] = relationship("User", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, timestamp={self.timestamp})>"
    
    def to_dict(self) -> dict:
        """Преобразует объект в словарь."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "context_used": self.context_used,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "processing_time": self.processing_time
        }
