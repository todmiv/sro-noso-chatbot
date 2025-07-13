from aiogram import Router, types

router = Router()


@router.message(commands={"help", "помощь"})
async def cmd_help(message: types.Message) -> None:
    """Отправляет список доступных команд."""
    help_text = (
        "/start – начать работу\n"
        "/help – справка\n"
        "/documents – список документов СРО\n"
        "/profile – ваш профиль\n"
        "/membership – статус членства\n"
        "Задайте вопрос в свободной форме для консультации."
    )
    await message.answer(help_text)
