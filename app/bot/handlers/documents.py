from aiogram import Router, types
from aiogram.filters import Command

from app.services.document_service import DocumentService

router = Router()


@router.message(Command("documents"))
async def cmd_documents(message: types.Message) -> None:
    """Показывает список доступных документов СРО."""
    document_service = DocumentService()
    
    documents = await document_service.get_active_documents()
    
    if not documents:
        await message.answer("📄 Документы временно недоступны.")
        return
    
    text = "📚 Доступные документы СРО НОСО:\n\n"
    for doc in documents[:10]:  # Показываем первые 10
        text += f"• {doc.title}\n"
    
    if len(documents) > 10:
        text += f"\n... и еще {len(documents) - 10} документов"
    
    text += "\n\nЗадайте вопрос по интересующему документу."
    
    await message.answer(text)
