#!/usr/bin/env python3
"""
Скрипт диагностики для проблемы с командой /profile
СРО НОСО чат-бот
"""

import asyncio
import inspect
from typing import get_type_hints

async def diagnose_profile_issue():
    """Диагностика проблемы с командой /profile"""
    
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМЫ /profile")
    print("=" * 50)
    
    try:
        # Проверка 1: Импорт UserService
        print("\n1. Проверка импорта UserService...")
        from app.services.userservice import UserService
        print("✅ UserService успешно импортирован")
        
        # Проверка 2: Сигнатура метода register_or_update_user
        print("\n2. Проверка сигнатуры register_or_update_user...")
        method = UserService.register_or_update_user
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        print(f"📋 Параметры метода: {params}")
        
        if 'organization_name' in params:
            print("✅ Параметр organization_name присутствует")
        else:
            print("❌ Параметр organization_name ОТСУТСТВУЕТ!")
            print("🔧 ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ:")
            print("   Добавьте organization_name: Optional[str] = None в сигнатуру метода")
        
        # Проверка 3: Type hints
        print("\n3. Проверка типов параметров...")
        try:
            hints = get_type_hints(method)
            for param, hint in hints.items():
                print(f"   {param}: {hint}")
        except Exception as e:
            print(f"⚠️  Не удалось получить type hints: {e}")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта UserService: {e}")
        return False
    
    try:
        # Проверка 4: Модель User
        print("\n4. Проверка модели User...")
        from app.models.user import User
        
        # Проверяем атрибуты модели
        user_attrs = [attr for attr in dir(User) if not attr.startswith('_')]
        print(f"📋 Атрибуты модели User: {user_attrs}")
        
        if hasattr(User, 'organization_name'):
            print("✅ Поле organization_name присутствует в модели")
        else:
            print("❌ Поле organization_name ОТСУТСТВУЕТ в модели!")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта модели User: {e}")
    
    try:
        # Проверка 5: База данных
        print("\n5. Проверка подключения к базе данных...")
        from app.database.connection import get_async_session
        from sqlalchemy import text
        
        async with get_async_session() as session:
            # Проверяем структуру таблицы users
            result = await session.execute(
                text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';")
            )
            columns = result.fetchall()
            
            print("📋 Структура таблицы users:")
            for col_name, col_type in columns:
                print(f"   {col_name}: {col_type}")
            
            # Проверяем наличие поля organization_name
            org_field_exists = any(col[0] == 'organization_name' for col in columns)
            if org_field_exists:
                print("✅ Поле organization_name присутствует в БД")
            else:
                print("❌ Поле organization_name ОТСУТСТВУЕТ в БД!")
                print("🔧 ТРЕБУЕТСЯ ВЫПОЛНИТЬ МИГРАЦИЮ:")
                print("   python -m alembic upgrade head")
                
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
    
    try:
        # Проверка 6: Profile handler
        print("\n6. Проверка profile handler...")
        from app.bot.handlers.profile import router as profile_router
        
        handlers = []
        for observer in [profile_router.message, profile_router.callback_query]:
            handlers.extend(observer.handlers)
        
        print(f"📋 Найдено {len(handlers)} обработчиков в profile router")
        
        # Ищем обработчик команды profile
        profile_handler = None
        for handler in handlers:
            if hasattr(handler, 'callback') and 'profile' in str(handler.callback.__name__):
                profile_handler = handler
                break
        
        if profile_handler:
            print("✅ Обработчик команды /profile найден")
        else:
            print("❌ Обработчик команды /profile НЕ НАЙДЕН!")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта profile handler: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("\n📋 РЕКОМЕНДАЦИИ:")
    print("1. Убедитесь что все параметры в UserService.register_or_update_user корректны")
    print("2. Проверьте что миграции БД выполнены")
    print("3. Перезапустите бота после внесения изменений")
    print("4. Проверьте логи в logs/bot.log для дополнительной информации")

if __name__ == "__main__":
    asyncio.run(diagnose_profile_issue())