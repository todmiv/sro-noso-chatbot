import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import aiohttp

from config.settings import config


class AlertSeverity(Enum):
    """Уровни важности алертов."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Структура алерта."""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertManager:
    """Менеджер алертов и уведомлений."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.handlers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация алертов
        self.webhook_url = getattr(config, 'alert_webhook_url', None)
        self.telegram_bot_token = getattr(config, 'alert_bot_token', None)
        self.telegram_chat_id = getattr(config, 'alert_chat_id', None)
        
        # Настройки дедупликации
        self.deduplication_window = timedelta(minutes=5)
        self.rate_limit_window = timedelta(minutes=1)
        self.rate_limit_count = 10
        
        # Счетчики для rate limiting
        self.alert_counts: Dict[str, List[datetime]] = {}
    
    def add_handler(self, handler: Callable[[Alert], None]) -> None:
        """Добавляет обработчик алертов."""
        self.handlers.append(handler)
    
    async def send_alert(
        self,
        alert_id: str,
        title: str,
        description: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        source: str = "system",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Отправляет алерт."""
        
        # Проверка rate limiting
        if not self._check_rate_limit(alert_id):
            self.logger.warning(f"Rate limit exceeded for alert {alert_id}")
            return False
        
        # Проверка дедупликации
        if self._is_duplicate(alert_id, title, description):
            self.logger.debug(f"Duplicate alert ignored: {alert_id}")
            return False
        
        # Создаем алерт
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {}
        )
        
        # Сохраняем алерт
        self.alerts[alert_id] = alert
        
        # Отправляем уведомления
        await self._process_alert(alert)
        
        # Вызываем обработчики
        for handler in self.handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
        
        return True
    
    def _check_rate_limit(self, alert_id: str) -> bool:
        """Проверяет rate limit для алерта."""
        now = datetime.now()
        
        # Очищаем старые записи
        if alert_id in self.alert_counts:
            self.alert_counts[alert_id] = [
                timestamp for timestamp in self.alert_counts[alert_id]
                if now - timestamp < self.rate_limit_window
            ]
        else:
            self.alert_counts[alert_id] = []
        
        # Проверяем лимит
        if len(self.alert_counts[alert_id]) >= self.rate_limit_count:
            return False
        
        # Добавляем текущий timestamp
        self.alert_counts[alert_id].append(now)
        return True
    
    def _is_duplicate(self, alert_id: str, title: str, description: str) -> bool:
        """Проверяет, является ли алерт дубликатом."""
        if alert_id not in self.alerts:
            return False
        
        existing_alert = self.alerts[alert_id]
        
        # Проверяем временное окно
        if datetime.now() - existing_alert.timestamp > self.deduplication_window:
            return False
        
        # Проверяем на точное совпадение
        return (
            existing_alert.title == title and
            existing_alert.description == description and
            not existing_alert.resolved
        )
    
    async def _process_alert(self, alert: Alert) -> None:
        """Обрабатывает алерт и отправляет уведомления."""
        tasks = []
        
        # Webhook уведомление
        if self.webhook_url:
            tasks.append(self._send_webhook_notification(alert))
        
        # Telegram уведомление
        if self.telegram_bot_token and self.telegram_chat_id:
            tasks.append(self._send_telegram_notification(alert))
        
        # Логирование
        tasks.append(self._log_alert(alert))
        
        # Выполняем все задачи параллельно
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_webhook_notification(self, alert: Alert) -> None:
        """Отправляет уведомление через webhook."""
        try:
            payload = {
                "id": alert.id,
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity.value,
                "timestamp": alert.timestamp.isoformat(),
                "source": alert.source,
                "metadata": alert.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Webhook notification sent for alert {alert.id}")
                    else:
                        self.logger.warning(f"Webhook notification failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {e}")
    
    async def _send_telegram_notification(self, alert: Alert) -> None:
        """Отправляет уведомление в Telegram."""
        try:
            # Форматируем сообщение
            severity_emoji = {
                AlertSeverity.LOW: "ℹ️",
                AlertSeverity.MEDIUM: "⚠️",
                AlertSeverity.HIGH: "🚨",
                AlertSeverity.CRITICAL: "💥"
            }
            
            message = (
                f"{severity_emoji.get(alert.severity, '❓')} **{alert.title}**\n\n"
                f"**Описание:** {alert.description}\n"
                f"**Серьезность:** {alert.severity.value.upper()}\n"
                f"**Источник:** {alert.source}\n"
                f"**Время:** {alert.timestamp.strftime('%d.%m.%Y %H:%M:%S')}"
            )
            
            if alert.metadata:
                message += f"\n**Метаданные:** {alert.metadata}"
            
            # Отправляем сообщение
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Telegram notification sent for alert {alert.id}")
                    else:
                        self.logger.warning(f"Telegram notification failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {e}")
    
    async def _log_alert(self, alert: Alert) -> None:
        """Логирует алерт."""
        log_message = f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.description}"
        
        if alert.severity == AlertSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif alert.severity == AlertSeverity.HIGH:
            self.logger.error(log_message)
        elif alert.severity == AlertSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Разрешает алерт."""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.now()
        
        self.logger.info(f"Alert {alert_id} resolved")
        return True
    
    def get_active_alerts(self) -> List[Alert]:
        """Получает активные алерты."""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Получает статистику алертов."""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        
        severity_counts = {}
        for alert in self.alerts.values():
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "severity_distribution": severity_counts,
            "last_alert_time": max(
                (alert.timestamp for alert in self.alerts.values()),
                default=None
            )
        }
    
    def cleanup_old_alerts(self, max_age: timedelta = timedelta(days=7)) -> int:
        """Очищает старые алерты."""
        cutoff_time = datetime.now() - max_age
        
        old_alerts = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.timestamp < cutoff_time and alert.resolved
        ]
        
        for alert_id in old_alerts:
            del self.alerts[alert_id]
        
        return len(old_alerts)


# Глобальный экземпляр менеджера алертов
alert_manager = AlertManager()


# Удобные функции для отправки алертов
async def send_error_alert(title: str, description: str, metadata: Dict[str, Any] = None) -> None:
    """Отправляет алерт об ошибке."""
    await alert_manager.send_alert(
        alert_id=f"error_{hash(title)}",
        title=title,
        description=description,
        severity=AlertSeverity.HIGH,
        source="application",
        metadata=metadata
    )


async def send_critical_alert(title: str, description: str, metadata: Dict[str, Any] = None) -> None:
    """Отправляет критический алерт."""
    await alert_manager.send_alert(
        alert_id=f"critical_{hash(title)}",
        title=title,
        description=description,
        severity=AlertSeverity.CRITICAL,
        source="application",
        metadata=metadata
    )


async def send_warning_alert(title: str, description: str, metadata: Dict[str, Any] = None) -> None:
    """Отправляет предупреждающий алерт."""
    await alert_manager.send_alert(
        alert_id=f"warning_{hash(title)}",
        title=title,
        description=description,
        severity=AlertSeverity.MEDIUM,
        source="application",
        metadata=metadata
    )


async def send_info_alert(title: str, description: str, metadata: Dict[str, Any] = None) -> None:
    """Отправляет информационный алерт."""
    await alert_manager.send_alert(
        alert_id=f"info_{hash(title)}",
        title=title,
        description=description,
        severity=AlertSeverity.LOW,
        source="application",
        metadata=metadata
    )
