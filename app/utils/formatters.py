from datetime import datetime, timedelta
from typing import Optional, Union
import locale


def format_datetime(dt: Optional[datetime], format_str: str = "%d.%m.%Y %H:%M") -> str:
    """Форматирует дату и время."""
    if dt is None:
        return "Не указано"
    
    try:
        return dt.strftime(format_str)
    except Exception:
        return "Ошибка формата"


def format_date(dt: Optional[datetime], format_str: str = "%d.%m.%Y") -> str:
    """Форматирует только дату."""
    return format_datetime(dt, format_str)


def format_time(dt: Optional[datetime], format_str: str = "%H:%M") -> str:
    """Форматирует только время."""
    return format_datetime(dt, format_str)


def format_duration(seconds: Union[int, float]) -> str:
    """Форматирует продолжительность в читаемый вид."""
    if seconds is None:
        return "Не указано"
    
    try:
        seconds = int(seconds)
        
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes} мин"
            return f"{minutes} мин {remaining_seconds} сек"
        elif seconds < 86400:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours} ч"
            return f"{hours} ч {remaining_minutes} мин"
        else:
            days = seconds // 86400
            remaining_hours = (seconds % 86400) // 3600
            if remaining_hours == 0:
                return f"{days} д"
            return f"{days} д {remaining_hours} ч"
    except Exception:
        return "Ошибка формата"


def format_file_size(size_bytes: Optional[int]) -> str:
    """Форматирует размер файла в читаемый вид."""
    if size_bytes is None:
        return "Не указано"
    
    try:
        size_bytes = int(size_bytes)
        
        if size_bytes < 1024:
            return f"{size_bytes} Б"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} КБ"
        elif size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f} МБ"
        else:
            return f"{size_bytes / (1024**3):.1f} ГБ"
    except Exception:
        return "Ошибка формата"


def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """Форматирует число с разделителями разрядов."""
    if number is None:
        return "Не указано"
    
    try:
        if decimals == 0:
            return f"{int(number):,}".replace(",", " ")
        else:
            return f"{float(number):,.{decimals}f}".replace(",", " ")
    except Exception:
        return "Ошибка формата"


def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
    """Форматирует процент."""
    if value is None:
        return "Не указано"
    
    try:
        return f"{float(value):.{decimals}f}%"
    except Exception:
        return "Ошибка формата"


def format_currency(amount: Union[int, float], currency: str = "₽") -> str:
    """Форматирует валюту."""
    if amount is None:
        return "Не указано"
    
    try:
        formatted_amount = format_number(amount, 2)
        return f"{formatted_amount} {currency}"
    except Exception:
        return "Ошибка формата"


def format_phone(phone: Optional[str]) -> str:
    """Форматирует номер телефона."""
    if not phone:
        return "Не указано"
    
    # Убираем все символы кроме цифр
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 11 and digits.startswith('7'):
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    elif len(digits) == 10:
        return f"+7 ({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    else:
        return phone


def format_telegram_username(username: Optional[str]) -> str:
    """Форматирует Telegram username."""
    if not username:
        return "Не указано"
    
    if username.startswith('@'):
        return username
    else:
        return f"@{username}"


def format_text_preview(text: Optional[str], max_length: int = 100) -> str:
    """Создает превью текста с ограничением длины."""
    if not text:
        return "Нет текста"
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def format_list(items: list, separator: str = ", ", empty_text: str = "Пусто") -> str:
    """Форматирует список в строку."""
    if not items:
        return empty_text
    
    return separator.join(str(item) for item in items)


def format_boolean(value: Optional[bool], true_text: str = "Да", false_text: str = "Нет") -> str:
    """Форматирует булево значение."""
    if value is None:
        return "Не указано"
    
    return true_text if value else false_text


def format_status(status: Optional[str]) -> str:
    """Форматирует статус с эмодзи."""
    if not status:
        return "❓ Не указано"
    
    status_map = {
        "active": "✅ Активен",
        "inactive": "❌ Неактивен",
        "pending": "⏳ В ожидании",
        "processing": "🔄 Обработка",
        "completed": "✅ Завершено",
        "failed": "❌ Ошибка",
        "cancelled": "🚫 Отменено"
    }
    
    return status_map.get(status.lower(), f"❓ {status}")


def format_rating(rating: Optional[float], max_rating: int = 5) -> str:
    """Форматирует рейтинг звездочками."""
    if rating is None:
        return "Не оценено"
    
    try:
        rating = float(rating)
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = max_rating - full_stars - half_star
        
        result = "⭐" * full_stars
        if half_star:
            result += "🌟"
        result += "☆" * empty_stars
        
        return f"{result} ({rating:.1f}/{max_rating})"
    except Exception:
        return "Ошибка формата"


def format_age(birth_date: Optional[datetime]) -> str:
    """Вычисляет и форматирует возраст."""
    if birth_date is None:
        return "Не указано"
    
    try:
        today = datetime.now()
        age = today.year - birth_date.year
        
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        if age < 0:
            return "Некорректная дата"
        
        return f"{age} лет"
    except Exception:
        return "Ошибка формата"


def format_relative_time(dt: Optional[datetime]) -> str:
    """Форматирует относительное время (например, "2 часа назад")."""
    if dt is None:
        return "Не указано"
    
    try:
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} дн. назад"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ч. назад"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} мин. назад"
        else:
            return "Только что"
    except Exception:
        return "Ошибка формата"
