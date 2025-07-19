from aiogram import Bot, Dispatcher, types
import asyncio

TOKEN = "7665546124:AAFUpZVhfS8xwP-GeX9-PmCLWOjclbojnzY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def any_message(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Тест", callback_data="test")]]
    )
    await message.answer("Тестовая кнопка", reply_markup=kb)

@dp.callback_query()
async def any_callback(callback: types.CallbackQuery):
    await callback.answer("callback получен!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())