import asyncio
from sqlalchemy import select
from app.database.connection import get_async_session
from app.models.user import User

async def show_organizations():
    async with get_async_session() as session:
        result = await session.execute(select(User.telegram_id, User.organization_name))
        users = result.all()
        
        print("\nOrganizations in database:")
        print("Telegram ID | Organization Name")
        print("-----------------------------")
        for user in users:
            print(f"{user.telegram_id} | {user.organization_name or 'None'}")

if __name__ == "__main__":
    asyncio.run(show_organizations())
