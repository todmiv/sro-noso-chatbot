from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def get_main_menu_keyboard(is_member: bool = False) -> InlineKeyboardMarkup:
    """Создает главное меню бота."""
    buttons = [
        [InlineKeyboardButton(text="📚 Документы", callback_data="documents")],
        [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🏢 Членство", callback_data="membership")]
    ]
    
    if is_member:
        buttons.append([InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")])
    
    buttons.append([InlineKeyboardButton(text="ℹ️ О СРО НОСО", callback_data="about_sro")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_profile_keyboard(is_member: bool = False) -> InlineKeyboardMarkup:
    """Создает клавиатуру для профиля."""
    buttons = [
        [InlineKeyboardButton(text="✏️ Редактировать организацию", callback_data="edit_organization")],
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_profile")],
    ]
    
    if not is_member:
        buttons.append([InlineKeyboardButton(text="📝 Подать заявку на вступление", callback_data="apply_membership")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_membership_keyboard(is_member: bool = False) -> InlineKeyboardMarkup:
    """Создает клавиатуру для раздела членства."""
    if is_member:
        buttons = [
            [InlineKeyboardButton(text="🔍 Проверить статус", callback_data="check_membership")],
            [InlineKeyboardButton(text="📋 Мои обязательства", callback_data="my_obligations")],
            [InlineKeyboardButton(text="💰 Взносы", callback_data="membership_fees")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="🎯 Преимущества членства", callback_data="membership_benefits")],
            [InlineKeyboardButton(text="📝 Требования для вступления", callback_data="membership_requirements")],
            [InlineKeyboardButton(text="📞 Контакты для вступления", callback_data="membership_contacts")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_documents_keyboard(categories: List[str] = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора категории документов."""
    buttons = []
    
    if categories:
        for category in categories:
            buttons.append([InlineKeyboardButton(text=f"📄 {category}", callback_data=f"doc_category_{category}")])
    else:
        # Стандартные категории
        buttons = [
            [InlineKeyboardButton(text="📄 Стандарты СРО", callback_data="doc_category_standards")],
            [InlineKeyboardButton(text="📋 Положения", callback_data="doc_category_regulations")],
            [InlineKeyboardButton(text="📝 Регламенты", callback_data="doc_category_procedures")],
            [InlineKeyboardButton(text="📊 Отчеты", callback_data="doc_category_reports")],
        ]
    
    buttons.append([InlineKeyboardButton(text="🔍 Поиск документов", callback_data="search_documents")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_consultation_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для консультаций."""
    buttons = [
        [InlineKeyboardButton(text="📋 Частые вопросы", callback_data="faq")],
        [InlineKeyboardButton(text="📞 Связаться с экспертом", callback_data="contact_expert")],
        [InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="leave_feedback")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str = "page"
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для пагинации."""
    buttons = []
    
    if total_pages <= 1:
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Кнопки навигации
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"{callback_prefix}_{current_page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"{callback_prefix}_{current_page + 1}"))
    
    buttons.append(nav_buttons)
    
    # Быстрая навигация
    if total_pages > 3:
        quick_nav = []
        if current_page > 2:
            quick_nav.append(InlineKeyboardButton(text="1", callback_data=f"{callback_prefix}_1"))
        if current_page < total_pages - 1:
            quick_nav.append(InlineKeyboardButton(text=str(total_pages), callback_data=f"{callback_prefix}_{total_pages}"))
        
        if quick_nav:
            buttons.append(quick_nav)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
