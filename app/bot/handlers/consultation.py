from aiogram import Router, types
from aiogram.filters import Command

from app.services.document_service import DocumentService

router = Router()


@router.message(Command(commands=['question']))
async def cmd_question(message: types.Message) -> None:
    """Обработчик консультационных вопросов."""
    if not message.text or len(message.text.split()) < 2:
        await message.answer(
            "❓ Пожалуйста, сформулируйте ваш вопрос.\n"
            "Пример: /question Какие требования к членству в СРО?"
        )
        return
    
    question = " ".join(message.text.split()[1:])
    
    # Показываем, что бот думает
    typing_message = await message.answer("🤔 Ищу информацию...")
    
    try:
        from app.services.global_services import services
        document_service = DocumentService()
        
        # Поиск релевантных документов
        context = await document_service.search_relevant_content(question)
        if not context:
            await typing_message.edit_text("📭 Не удалось найти релевантные документы.")
            return
            
        # Генерация ответа с помощью ИИ
        response = await services.rag_system.generate_response(
            question=question,
            context=context,
            user_id=message.from_user.id
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Задать новый вопрос", callback_data="new_question")],
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
            [InlineKeyboardButton(text="Связаться с поддержкой", url="https://t.me/your_support_bot")]
        ])
        await typing_message.edit_text(response, reply_markup=menu_keyboard)
        
    except Exception as e:
        print(f"[ERROR][consultation] {e}")
        await typing_message.edit_text(
            "❌ Произошла ошибка при обработке запроса. "
            "Попробуйте позже или обратитесь в службу поддержки."
        )


from aiogram import F

@router.callback_query(F.data == "new_question")
async def handle_new_question(callback: types.CallbackQuery):
    await callback.message.answer("Пожалуйста, введите ваш новый вопрос.")
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def handle_main_menu(callback: types.CallbackQuery):
    try:
        from app.bot.keyboards.inline_keyboards import get_main_menu_keyboard
        await callback.message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    except Exception:
        await callback.message.answer("Главное меню. Выберите действие.")
    await callback.answer()

@router.message(lambda message: not (message.text and message.text.startswith('/')))
async def handle_free_text(message: types.Message) -> None:
    """Обработчик свободного текста как консультационного вопроса."""
    if message.text and len(message.text) > 10:
        # Передаем в консультационный сервис
        await cmd_question(message)
