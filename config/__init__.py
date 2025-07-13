"""Пакет конфигурации приложения."""
from .settings import config
from .database import DatabaseConfig, RedisConfig

__all__ = ["config", "DatabaseConfig", "RedisConfig"]
