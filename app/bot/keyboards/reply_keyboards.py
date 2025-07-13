from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную reply-клавиатуру."""
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📚 Документы"),
        KeyboardButton(text="❓ Помощь"),
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="🏢 Членство")
    )
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_member_reply_keyboard() -> ReplyKeyboardMarkup:
    """Создает reply-клавиатуру для членов СРО."""
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📚 Документы"),
        KeyboardButton(text="❓ Консультация"),
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="🏢 Членство"),
        KeyboardButton(text="🔔 Уведомления"),
        KeyboardButton(text="📊 Отчеты")
    )
    
    builder.adjust(2, 2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_admin_reply_keyboard() -> ReplyKeyboardMarkup:
    """Создает reply-клавиатуру для администраторов."""
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📚 Документы"),
        KeyboardButton(text="👥 Пользователи"),
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="🔔 Рассылка"),
        KeyboardButton(text="⚙️ Настройки"),
        KeyboardButton(text="📝 Логи")
    )
    
    builder.adjust(2, 2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для отправки контакта."""
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📞 Отправить контакт", request_contact=True),
        KeyboardButton(text="❌ Отмена")
    )
    
    builder.adjust(1, 1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для отправки местоположения."""
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📍 Отправить местоположение", request_location=True),
        KeyboardButton(text="❌ Отмена")
    )
    
    builder.adjust(1, 1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру Да/Нет."""
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="✅ Да"),
        KeyboardButton(text="❌ Нет")
    )
    
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
