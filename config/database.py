from dataclasses import dataclass
import os


@dataclass
class DatabaseConfig:
    """Конфигурация подключения к базе данных."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Создает конфигурацию из переменных окружения."""
        url = os.getenv('DATABASE_URL')
        if not url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        return cls(
            url=url,
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30'))
        )


@dataclass 
class RedisConfig:
    """Конфигурация подключения к Redis."""
    url: str
    
    @classmethod
    def from_env(cls) -> 'RedisConfig':
        """Создает конфигурацию из переменных окружения."""
        url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        return cls(url=url)
