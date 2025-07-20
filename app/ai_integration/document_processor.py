from pathlib import Path
from typing import Generator, List
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
    def split_into_chunks(
        text: str, 
        max_tokens: int = 1000,
        preserve_sentences: bool = True
    ) -> Generator[str, None, None]:
        """Разбивает текст на чанки по токенам с возможностью сохранения целостности предложений.
        
        Args:
            text: Входной текст для разбиения
            max_tokens: Максимальное количество токенов в чанке
            preserve_sentences: Сохранять ли целостность предложений (по умолчанию True)
            
        Yields:
            str: Текстовые чанки
            
        Note:
            Под токенами понимаются слова и пробелы между ними.
            При preserve_sentences=True разбиение происходит по границам предложений.
        """
        if not text.strip():
            return

        if preserve_sentences:
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                sentence_size = len(sentence.split())
                if current_size + sentence_size > max_tokens:
                    if current_chunk:
                        yield ' '.join(current_chunk)
                    current_chunk = [sentence]
                    current_size = sentence_size
                else:
                    current_chunk.append(sentence)
                    current_size += sentence_size
                    
            if current_chunk:
                yield ' '.join(current_chunk)
        else:
            words = text.split()
            chunk, current = [], 0
            for word in words:
                if current + len(word.split()) >= max_tokens:
                    yield " ".join(chunk)
                    chunk, current = [word], len(word.split())
                else:
                    chunk.append(word)
                    current += len(word.split())
            if chunk:
                yield " ".join(chunk)
