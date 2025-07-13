from aiogram import Router, types
from aiogram.filters import CommandStart

from app.services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    """Обработчик команды /start."""
    user_service = UserService()
    
    # Регистрируем или обновляем пользователя
    await user_service.register_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    welcome_text = (
        "👋 Добро пожаловать в чат-бот СРО НОСО!\n\n"
        "Я помогу вам получить информацию о:\n"
        "• Документах и стандартах СРО\n"
        "• Требованиях к членству\n"
        "• Процедурах и регламентах\n"
        "• Ответах на вопросы по строительной деятельности\n\n"
        "Используйте /help для списка доступных команд."
    )
    
    await message.answer(welcome_text)
