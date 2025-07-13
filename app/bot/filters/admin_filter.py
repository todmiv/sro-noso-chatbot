from typing import Union, List
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from config.settings import config


class AdminFilter(Filter):
    """Фильтр для проверки администраторских прав."""
    
    def __init__(self, admin_ids: List[int] = None):
        self.admin_ids = admin_ids or getattr(config, 'admin_ids', [])
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Проверяет, является ли пользователь администратором."""
        user_id = event.from_user.id
        return user_id in self.admin_ids


class SuperAdminFilter(Filter):
    """Фильтр для проверки супер-администраторских прав."""
    
    def __init__(self, super_admin_ids: List[int] = None):
        self.super_admin_ids = super_admin_ids or getattr(config, 'super_admin_ids', [])
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Проверяет, является ли пользователь супер-администратором."""
        user_id = event.from_user.id
        return user_id in self.super_admin_ids
