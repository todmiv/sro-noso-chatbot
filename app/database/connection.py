import time
import asyncio
import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as aioredis

from config.settings import config

logger = logging.getLogger(__name__)

# Глобальные переменные для подключений
_engine: AsyncEngine = None
_session_factory: sessionmaker = None
_redis_client: aioredis.Redis = None


async def wait_for_redis(timeout: int = 30) -> None:
    """Ожидает доступности Redis."""
    redis_url = config.redis.url
    deadline = time.monotonic() + timeout
    
    logger.info(f"Waiting for Redis at {redis_url}...")
    
    while time.monotonic() < deadline:
        try:
            temp_client = aioredis.from_url(
                redis_url, 
                encoding="utf8", 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            await temp_client.ping()
            await temp_client.aclose()
            logger.info("Redis is available")
            return
        except Exception as e:
            logger.debug(f"Redis connection attempt failed: {e}")
            await asyncio.sleep(2)
    
    raise RuntimeError(f"Redis at {redis_url} is unreachable after {timeout}s")


async def init_redis() -> aioredis.Redis:
    """Инициализирует подключение к Redis."""
    global _redis_client
    
    if _redis_client is None:
        await wait_for_redis()
        _redis_client = aioredis.from_url(
            config.redis.url,
            encoding="utf8",
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True
        )
        logger.info("Redis client initialized")
    
    return _redis_client


def get_engine() -> AsyncEngine:
    """Возвращает экземпляр движка базы данных."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            config.database.url,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout,
            echo=config.debug
        )
        logger.info("Database engine initialized")
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
    
    logger.info("Database initialized")


async def close_database() -> None:
    """Закрывает соединения с базой данных."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")


async def close_redis() -> None:
    """Закрывает соединение с Redis."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed")


def get_redis() -> aioredis.Redis:
    """Возвращает Redis клиент."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client
