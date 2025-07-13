from pathlib import Path
from typing import List

import pdfplumber


class DocumentProcessor:
    """Извлечение текста из PDF-документов."""

    @staticmethod
    def extract_text(file_path: Path) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text

    @staticmethod
    def split_into_chunks(text: str, max_tokens: int = 1000) -> List[str]:
        words = text.split()
        chunk, current = [], 0
        for word in words:
            if current + len(word) >= max_tokens:
                yield " ".join(chunk)
                chunk, current = [word], len(word)
            else:
                chunk.append(word)
                current += len(word)
        if chunk:
            yield " ".join(chunk)
