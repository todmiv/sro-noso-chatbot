from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from config.settings import config

_engine: AsyncEngine | None = None
async_session = sessionmaker(class_= "AsyncSession", expire_on_commit=False)

def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(config.database.url, pool_size=10)
    return _engine

async def init_database() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        # Импортируется Base из моделей, чтобы создать все таблицы
        from app.models.base import Base  
        await conn.run_sync(Base.metadata.create_all)
