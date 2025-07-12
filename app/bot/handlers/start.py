from aiogram import Router, types

router = Router()

@router.message(commands={"start", "старт"})
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Добро пожаловать в чат-бот СРО НОСО!\n"
        "Введите /help для списка команд."
    )
