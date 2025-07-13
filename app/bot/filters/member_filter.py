from typing import Union
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from app.services.auth_service import AuthService
from app.services.user_service import UserService


class MemberFilter(Filter):
    """Фильтр для проверки членства в СРО."""
    
    def __init__(self, is_member: bool = True):
        self.is_member = is_member
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Проверяет, является ли пользователь членом СРО."""
        user_service = UserService()
        auth_service = AuthService(user_service)
        
        user_id = event.from_user.id
        user_is_member = await auth_service.is_member(user_id)
        
        return user_is_member == self.is_member
