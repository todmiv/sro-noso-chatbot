import logging
from aiogram import Router, types
from aiogram.filters import Command

from app.services.user_service import UserService

print("[IMPORT] secret.py imported")
ADMIN_TELEGRAM_ID = 1698252330

logger = logging.getLogger(__name__)
router = Router()
logger.info("Secret router initialized")


@router.message(Command(commands=["test"]))
async def test_command(message: types.Message):
    print("TEST COMMAND RECEIVED")
    await message.answer("Тестовая команда работает")

@router.message(Command(commands=["allusers"]))
async def all_users_handler(message: types.Message):
    logger.info(f"/allusers called by user: {message.from_user.id}")
    print(f"/allusers called by user: {message.from_user.id}")
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        print("Access denied for /allusers")
        await message.answer("⛔️ Доступ запрещён.")
        return
    try:
        user_service = UserService()
        users = await user_service.get_all_users()
        print(f"users fetched: {len(users)}")
        if not users:
            await message.answer("Пользователей не найдено.")
            print("No users found")
            return
        lines = [
            f"Всего пользователей: {len(users)}\n"
        ]
        for user in users:
            lines.append(
                f"ID: {user.telegram_id}, "
                f"Имя: {user.first_name or '-'}, "
                f"Фамилия: {user.last_name or '-'}, "
                f"Username: @{user.username or '-'}"
            )
        text = '\n'.join(lines)
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await message.answer(chunk)
        print("/allusers finished sending")
    except Exception as e:
        print(f"/allusers error: {e}")
        await message.answer(f"Ошибка: {e}")
