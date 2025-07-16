import asyncio
from app.database.connection import get_engine, get_session_factory, close_database
from sqlalchemy import text

async def test_postgres_connection():
    try:
        # Get engine and test connection
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("PostgreSQL connection test:", result.scalar() == 1)
        
        # Test session factory
        session_factory = get_session_factory()
        async with session_factory() as session:
            result = await session.execute(text("SELECT version()"))
            print("PostgreSQL version:", result.scalar())
        
        return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {str(e)}")
        return False
    finally:
        await close_database()

if __name__ == "__main__":
    result = asyncio.run(test_postgres_connection())
    print(f"PostgreSQL connection test {'passed' if result else 'failed'}")
