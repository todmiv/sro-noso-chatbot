from typing import List, Optional
import asyncio
from aiogram import Bot
from datetime import datetime, timedelta

from config.settings import config
from app.database.connection import get_async_session
from app.database.repositories.user_repository import UserRepository
from app.models.user import User


class NotificationService:
    """Сервис для отправки уведомлений пользователям."""
    
    def __init__(self):
        self.bot = Bot(token=config.bot.token)
        self.admin_ids = getattr(config, 'admin_ids', [])
    
    async def send_notification_to_user(self, user_id: int, message: str) -> bool:
        """Отправляет уведомление конкретному пользователю."""
        try:
            await self.bot.send_message(user_id, message)
            return True
        except Exception as e:
            print(f"Failed to send notification to user {user_id}: {e}")
            return False
    
    async def send_notification_to_members(self, message: str) -> int:
        """Отправляет уведомление всем членам СРО."""
        sent_count = 0
        
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            members = await user_repo.get_members()
            
            for member in members:
                if await self.send_notification_to_user(member.telegram_id, message):
                    sent_count += 1
                    # Небольшая задержка для избежания лимитов
                    await asyncio.sleep(0.1)
        
        return sent_count
    
    async def send_notification_to_all_users(self, message: str) -> int:
        """Отправляет уведомление всем пользователям."""
        sent_count = 0
        
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            users = await user_repo.get_all_active_users()
            
            for user in users:
                if await self.send_notification_to_user(user.telegram_id, message):
                    sent_count += 1
                    # Небольшая задержка для избежания лимитов
                    await asyncio.sleep(0.1)
        
        return sent_count
    
    async def notify_admins_about_error(
        self, 
        error: str, 
        user_id: Optional[int] = None, 
        update_id: Optional[int] = None
    ) -> None:
        """Уведомляет администраторов об ошибке."""
        error_message = (
            f"🚨 **Ошибка в боте**\n\n"
            f"**Время:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            f"**Ошибка:** {error}\n"
        )
        
        if user_id:
            error_message += f"**Пользователь:** {user_id}\n"
        
        if update_id:
            error_message += f"**Update ID:** {update_id}\n"
        
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(admin_id, error_message, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")
    
    async def notify_about_new_user(self, user: User) -> None:
        """Уведомляет администраторов о новом пользователе."""
        message = (
            f"👤 **Новый пользователь**\n\n"
            f"**Имя:** {user.first_name} {user.last_name or ''}\n"
            f"**Username:** @{user.username or 'не указан'}\n"
            f"**Telegram ID:** {user.telegram_id}\n"
            f"**Организация:** {user.organization_name or 'не указана'}\n"
            f"**Дата регистрации:** {user.registration_date.strftime('%d.%m.%Y %H:%M')}"
        )
        
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(admin_id, message, parse_mode="Markdown")
            except Exception:
                pass
    
    async def notify_about_document_update(self, document_title: str, document_id: int) -> int:
        """Уведомляет пользователей об обновлении документа."""
        message = (
            f"📄 **Обновление документа**\n\n"
            f"Обновлен документ: **{document_title}**\n\n"
            f"Используйте команду /documents для просмотра изменений."
        )
        
        # Отправляем всем членам СРО
        return await self.send_notification_to_members(message)
    
    async def send_scheduled_reminder(self, reminder_text: str, target_group: str = "members") -> int:
        """Отправляет запланированное напоминание."""
        message = f"🔔 **Напоминание**\n\n{reminder_text}"
        
        if target_group == "members":
            return await self.send_notification_to_members(message)
        elif target_group == "all":
            return await self.send_notification_to_all_users(message)
        else:
            return 0
    
    async def notify_about_system_maintenance(self, start_time: datetime, duration: timedelta) -> int:
        """Уведомляет о технических работах."""
        end_time = start_time + duration
        
        message = (
            f"🛠️ **Технические работы**\n\n"
            f"**Начало:** {start_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"**Окончание:** {end_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"**Продолжительность:** {duration.seconds // 3600} ч {(duration.seconds % 3600) // 60} мин\n\n"
            f"В это время бот может работать нестабильно. Приносим извинения за неудобства."
        )
        
        return await self.send_notification_to_all_users(message)
    
    async def send_membership_expiration_warning(self, user_id: int, days_left: int) -> bool:
        """Отправляет предупреждение об истечении членства."""
        message = (
            f"⚠️ **Предупреждение о членстве**\n\n"
            f"Ваше членство в СРО НОСО истекает через {days_left} дней.\n\n"
            f"Для продления обратитесь в офис СРО или воспользуйтесь личным кабинетом на сайте."
        )
        
        return await self.send_notification_to_user(user_id, message)
    
    async def close(self) -> None:
        """Закрывает соединение с ботом."""
        await self.bot.session.close()
