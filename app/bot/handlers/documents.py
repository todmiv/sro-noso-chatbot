from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from app.services.document_service import DocumentService
from app.database.connection import get_async_session
from app.database.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command(commands=['documents']))
async def cmd_documents(message: types.Message) -> None:
    """Показывает список доступных документов СРО."""
    document_service = DocumentService()
    
    documents = await document_service.get_active_documents()
    
    if not documents:
        await message.answer("📄 Документы временно недоступны.")
        return
    
    # Группируем документы по категориям
    categories = {}
    for doc in documents:
        if doc.category not in categories:
            categories[doc.category] = []
        categories[doc.category].append(doc)
    
    text = "📚 Доступные документы СРО НОСО:\n\n"
    for category, docs in categories.items():
        text += f"<b>{category}</b>:\n"
        for doc in docs[:5]:  # Показываем первые 5 в каждой категории
            text += f"• {doc.title}\n"
        if len(docs) > 5:
            text += f"  ... и еще {len(docs) - 5} документов\n"
        text += "\n"
    
    text += "\nВыберите документ для скачивания."
    
    # Создаем клавиатуру с категориями
    builder = InlineKeyboardBuilder()
    for category in categories.keys():
        builder.button(text=category, callback_data=f"doc_category:{category}")
    builder.adjust(2)
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("doc_category:"))
async def show_category_documents(callback: types.CallbackQuery):
    """Показывает документы выбранной категории."""
    try:
        await callback.answer("Обработка...")  # Проверка вызова
        import logging
        logger = logging.getLogger(__name__)
        category = callback.data.split(":")[1]
        print(f"[doc_category] callback: category={category}")
        document_service = DocumentService()
        
        documents = await document_service.get_active_documents()
        print(f"[doc_category] all_categories: {[doc.category for doc in documents]}")
        logger.info(f"[doc_category] callback: category={category}, all_categories={[doc.category for doc in documents]}")
        category_docs = [doc for doc in documents if doc.category == category]
        
        if not category_docs:
            print(f"[doc_category] Нет документов в категории: {category}")
            logger.warning(f"[doc_category] Нет документов в категории: {category}")
            await callback.answer("Нет документов в этой категории")
            return
        
        builder = InlineKeyboardBuilder()
        for doc in category_docs:
            builder.button(text=doc.title, callback_data=f"doc_download:{doc.id}")
        builder.adjust(1)
        
        await callback.message.edit_text(
            f"📂 Документы категории <b>{category}</b>:",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
    except Exception as e:
        print(f"[doc_category] Exception: {e}")
        await callback.answer(f"Ошибка обработки категории: {e}")

@router.callback_query(F.data.startswith("doc_download:"))
async def download_document(callback: types.CallbackQuery):
    """Обрабатывает скачивание документа."""
    doc_id = int(callback.data.split(":")[1])
    document_service = DocumentService()
    
    document = await document_service.get_document_by_id(doc_id)
    if not document:
        await callback.answer("Документ не найден")
        return
    
    file_path = await document_service.get_document_file(document)
    if not file_path:
        await callback.answer("Файл документа недоступен")
        return
    
    try:
        # Увеличиваем счетчик скачиваний
        async with get_async_session() as session:
            doc_repo = DocumentRepository(session)
            await doc_repo.increment_download_count(doc_id)
        
        with open(file_path, "rb") as file:
            await callback.message.answer_document(
                types.BufferedInputFile(
                    file.read(),
                    filename=f"{document.title}.{document.file_extension}"
                ),
                caption=f"📄 {document.title}\n\n{document.description or ''}"
            )
        await callback.answer()
    except Exception as e:
        await callback.answer("Ошибка при загрузке документа")
        # Логируем ошибку
        logger.error(f"Error downloading document {doc_id}: {str(e)}")
