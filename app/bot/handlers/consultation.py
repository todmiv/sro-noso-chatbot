from aiogram import Router, types
from aiogram.filters import Command

from app.services.ai_service import AIService
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
        ai_service = AIService()
        document_service = DocumentService()
        
        # Поиск релевантных документов
        context = await document_service.search_relevant_content(question)
        if not context:
            await typing_message.edit_text("📭 Не удалось найти релевантные документы.")
            return
            
        # Генерация ответа с помощью ИИ
        response = await ai_service.generate_consultation_response(
            user_question=question,
            user_id=message.from_user.id,
            context=context
        )
        
        await typing_message.edit_text(response)
        
    except Exception as e:
        await typing_message.edit_text(
            "❌ Произошла ошибка при обработке запроса. "
            "Попробуйте позже или обратитесь в службу поддержки."
        )


@router.message()
async def handle_free_text(message: types.Message) -> None:
    """Обработчик свободного текста как консультационного вопроса."""
    if message.text and len(message.text) > 10:
        # Передаем в консультационный сервис
        await cmd_question(message)
