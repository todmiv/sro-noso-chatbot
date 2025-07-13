"""Клавиатуры для телеграм-бота."""
from .inline_keyboards import (
    get_main_menu_keyboard,
    get_profile_keyboard,
    get_membership_keyboard,
    get_documents_keyboard,
    get_consultation_keyboard
)
from .reply_keyboards import (
    get_main_reply_keyboard,
    get_member_reply_keyboard,
    get_admin_reply_keyboard
)

__all__ = [
    "get_main_menu_keyboard",
    "get_profile_keyboard", 
    "get_membership_keyboard",
    "get_documents_keyboard",
    "get_consultation_keyboard",
    "get_main_reply_keyboard",
    "get_member_reply_keyboard",
    "get_admin_reply_keyboard"
]
