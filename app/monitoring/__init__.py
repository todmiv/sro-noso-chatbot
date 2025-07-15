"""Модуль мониторинга и метрик."""
from .metrics import (
    REQUEST_COUNT,
    RESPONSE_TIME,
    setup_metrics
)
from .health_check import health_check_handler            # , setup_health_check
from .alerts import AlertManager

__all__ = [
    "REQUEST_COUNT",
    "RESPONSE_TIME",
    "setup_metrics",
    "health_check_handler",
    # "setup_health_check",                                 # Временно отключено
    "AlertManager"
]
