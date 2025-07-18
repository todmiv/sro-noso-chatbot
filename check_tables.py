from app.database.connection import get_engine
import asyncio
from sqlalchemy import inspect

async def check_tables():
    engine = get_engine()
    async with engine.connect() as conn:
        inspector = inspect(conn.sync_engine)
        print('Tables:', inspector.get_table_names())
        print('Users columns:', inspector.get_columns('users'))
        print('Feedback columns:', inspector.get_columns('feedback'))

asyncio.run(check_tables())
