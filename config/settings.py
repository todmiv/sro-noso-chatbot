import os
from pathlib import Path
from typing import Optional
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            url=cls._get_required_env('DATABASE_URL'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30'))
        )
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

@dataclass
class BotConfig:
    """Конфигурация Telegram бота"""
    token: str
    username: str
    webhook_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        return cls(
            token=cls._get_required_env('BOT_TOKEN'),
            username=os.getenv('BOT_USERNAME', ''),
            webhook_url=os.getenv('WEBHOOK_URL')
        )
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

@dataclass
class AIConfig:
    """Конфигурация ИИ сервиса"""
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        return cls(
            api_key=cls._get_required_env('DEEPSEEK_API_KEY'),
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
            model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '2000')),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.7'))
        )
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

@dataclass
class SecurityConfig:
    """Конфигурация безопасности"""
    secret_key: str
    jwt_secret: str
    session_timeout: int = 3600
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        return cls(
            secret_key=cls._get_required_env('SECRET_KEY'),
            jwt_secret=cls._get_required_env('JWT_SECRET'),
            session_timeout=int(os.getenv('SESSION_TIMEOUT', '3600'))
        )
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    environment: str
    debug: bool
    log_level: str
    base_dir: Path
    
    # Подключаемые конфигурации
    database: DatabaseConfig
    bot: BotConfig
    ai: AIConfig
    security: SecurityConfig
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """Загружает конфигурацию из переменных окружения"""
        environment = os.getenv('ENVIRONMENT', 'development')
        
        return cls(
            environment=environment,
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            base_dir=Path(__file__).parent.parent,
            database=DatabaseConfig.from_env(),
            bot=BotConfig.from_env(),
            ai=AIConfig.from_env(),
            security=SecurityConfig.from_env()
        )
    
    @property
    def is_production(self) -> bool:
        return self.environment == 'production'
    
    @property
    def is_development(self) -> bool:
        return self.environment == 'development'

# Глобальный экземпляр конфигурации
try:
    config = AppConfig.load()
except ValueError as e:
    logging.error(f"Configuration error: {e}")
    raise

# Валидация конфигурации
def validate_config():
    """Проверяет корректность загруженной конфигурации"""
    errors = []
    
    # Проверка токена бота
    if not config.bot.token or len(config.bot.token) < 10:
        errors.append("Invalid bot token")
    
    # Проверка API ключа DeepSeek
    if not config.ai.api_key or len(config.ai.api_key) < 10:
        errors.append("Invalid DeepSeek API key")
    
    # Проверка секретных ключей
    if len(config.security.secret_key) < 32:
        errors.append("Secret key too short (minimum 32 characters)")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

# Выполняем валидацию при импорте
validate_config()
