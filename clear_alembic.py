from app.database.connection import get_engine
import asyncio
from sqlalchemy import text

async def clear_alembic():
    engine = get_engine()
    async with engine.connect() as conn:
        await conn.execute(text('DELETE FROM alembic_version'))
        await conn.commit()

asyncio.run(clear_alembic())
