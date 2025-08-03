from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.models.base import Base


class ErrorLog(Base):
    """Модель для хранения логов ошибок."""
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    traceback = Column(Text)
    user_id = Column(Integer, nullable=True)
    update_id = Column(Integer, nullable=True)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ErrorLog {self.error_type}: {self.error_message[:50]}...>"
