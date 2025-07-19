from pathlib import Path
from typing import List
import docx
import pdfplumber


class DocumentProcessor:
    """Извлечение текста из документов различных форматов."""

    @staticmethod
    def extract_text(file_path: Path) -> str:
        """Извлекает текст из файла в зависимости от его расширения."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            return text
            
        elif suffix in ('.docx', '.doc'):
            if suffix == '.docx':
                doc = docx.Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs])
            else:
                raise ValueError("DOC format requires additional dependencies")
                
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

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
