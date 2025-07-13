import re
from typing import Any

TELEGRAM_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{5,32}$")


def validate_username(value: str) -> None:
    if not TELEGRAM_USERNAME_RE.match(value):
        raise ValueError("Неверный формат username")


def ensure_not_none(value: Any, field: str) -> None:
    if value is None:
        raise ValueError(f"{field} не может быть пустым")
