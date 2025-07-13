from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.settings import config

# Глобальные переменные для подключения
_engine: AsyncEngine = None
_session_factory: sessionmaker = None


def get_engine() -> AsyncEngine:
    """Возвращает экземпляр движка базы данных."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            config.database.url,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout,
            echo=config.debug  # Логируем SQL в режиме отладки
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Возвращает фабрику сессий."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            class_=AsyncSession,
            bind=get_engine(),
            expire_on_commit=False
        )
    return _session_factory


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    """Контекстный менеджер для получения асинхронной сессии."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Инициализирует базу данных, создавая все таблицы."""
    from app.models.base import Base
    
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """Закрывает соединения с базой данных."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
