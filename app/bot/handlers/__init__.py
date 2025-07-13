"""Регистрация всех обработчиков команд."""
from aiogram import Dispatcher

from .start import router as start_router
from .help import router as help_router
from .documents import router as documents_router
from .consultation import router as consultation_router
from .profile import router as profile_router
from .membership import router as membership_router
from .error_handler import router as error_router


def register_handlers(dp: Dispatcher) -> None:
    """Регистрирует все роутеры в диспетчере."""
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(documents_router)
    dp.include_router(consultation_router)
    dp.include_router(profile_router)
    dp.include_router(membership_router)
    dp.include_router(error_router)
