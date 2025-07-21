import asyncio
from app.database.connection import get_engine

async def show_users_table():
    engine = get_engine()
    async with engine.begin() as conn:
        result = await conn.execute(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
            """
        )
        rows = result.fetchall()
        print("users table structure:")
        for row in rows:
            print(row)

if __name__ == "__main__":
    asyncio.run(show_users_table())
