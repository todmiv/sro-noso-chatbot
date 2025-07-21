"""Регистрация всех обработчиков команд."""
from aiogram import Dispatcher

from .start import router as start_router
from .help import router as help_router
from .documents import router as documents_router
from .consultation import router as consultation_router
from .profile import router as profile_router
from .membership import router as membership_router
from .error_handler import router as error_router
print("[IMPORT] secret.py will be imported as secret_router")
from .secret import router as secret_router


def register_handlers(dp: Dispatcher) -> None:
    """Регистрирует все роутеры в диспетчере."""
    print("[REGISTER] start_router")
    dp.include_router(start_router)
    print("[REGISTER] help_router")
    dp.include_router(help_router)
    print("[REGISTER] documents_router")
    dp.include_router(documents_router)
    print("[REGISTER] consultation_router")
    dp.include_router(consultation_router)
    print("[REGISTER] profile_router")
    dp.include_router(profile_router)
    print("[REGISTER] membership_router")
    dp.include_router(membership_router)
    print("[REGISTER] secret_router")
    dp.include_router(secret_router)
    print("[REGISTER] error_router")
    dp.include_router(error_router)
