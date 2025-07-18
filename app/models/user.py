from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, Boolean, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    is_member: Mapped[bool] = mapped_column(Boolean, default=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="user")
    feedback: Mapped[List["Feedback"]] = relationship("Feedback", back_populates="user")
