import asyncio
import os
from pathlib import Path
from datetime import datetime

from app.database.connection import get_async_session
from app.database.repositories.document_repository import DocumentRepository
from app.models.document import Document

DOCUMENTS_PATH = Path('data/documents')

def get_document_info(file_path: Path):
    """Извлекает базовую информацию о документе по файлу."""
    rel_path = file_path.relative_to(DOCUMENTS_PATH)
    return {
        'title': file_path.stem,
        'file_path': str(rel_path),
        'document_type': file_path.suffix[1:] if file_path.suffix else 'unknown',
        'description': '',
        'category': rel_path.parts[0] if len(rel_path.parts) > 1 else '',
        'tags': '',
        'is_active': True,
        'is_public': True,
        'upload_date': datetime.utcnow(),
        'last_updated': datetime.utcnow(),
        'file_size': file_path.stat().st_size,
        'download_count': 0,
        'version': '1.0',
        'content_hash': '',
    }

async def import_documents():
    files = [f for f in DOCUMENTS_PATH.rglob('*') if f.is_file()]
    if not files:
        print('Нет файлов для импорта.')
        return
    async with get_async_session() as session:
        repo = DocumentRepository(session)
        for file in files:
            info = get_document_info(file)
            # Проверка на дублирование по относительному пути
            existing = await repo.get_by_title(info['title'])
            if existing:
                print(f"Документ '{info['title']}' уже существует, пропускаем.")
                continue
            doc = Document(**info)
            await repo.save(doc)
            print(f"Импортирован документ: {info['title']} ({info['file_path']})")

if __name__ == "__main__":
    asyncio.run(import_documents())
