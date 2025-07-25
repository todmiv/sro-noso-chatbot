import asyncio
from sqlalchemy import select
from app.database.connection import get_async_session
from app.models.user import User

async def clear_organization():
    async with get_async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == 1698252330))
        user = result.scalars().first()
        if user:
            user.organization_name = None
            await session.commit()
            print(f"Cleared organization for user {user.telegram_id}")
        else:
            print("User not found")

if __name__ == "__main__":
    asyncio.run(clear_organization())
