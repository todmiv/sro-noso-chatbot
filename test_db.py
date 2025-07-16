import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import socket
from datetime import datetime
import sys
import io

# Настройка кодировки вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Загружаем переменные окружения
load_dotenv()

async def test_database():
    print("\n=== Начало тестирования подключения к PostgreSQL ===")
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Шаг 1: Проверка доступности хоста
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        
        print(f"\n[1/5] Проверка доступности {host}:{port}...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex((host, port))
            if result == 0:
                print(f"[OK] Порт {port} доступен на {host}")
            else:
                print(f"[ERROR] Не удалось подключиться к {host}:{port}")
                return

        # Шаг 2: Проверка переменных окружения
        print("\n[2/5] Проверка переменных окружения...")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_name = os.getenv("DB_NAME", "sro_chatbot")
        
        print(f"Пользователь: {db_user}")
        print(f"База данных: {db_name}")
        print("Пароль: " + ("установлен" if db_password else "не установлен"))

        # Шаг 3: Подключение к PostgreSQL
        print("\n[3/5] Попытка подключения к PostgreSQL...")
        try:
            conn = await asyncpg.connect(
                host=host,
                port=port,
                user=db_user,
                password=db_password,
                database=db_name,
                timeout=10
            )
            print("[OK] Подключение установлено")
        except Exception as e:
            print(f"[ERROR] Ошибка подключения: {type(e).__name__}: {e}")
            return

        # Шаг 4: Проверка версии PostgreSQL
        print("\n[4/5] Проверка версии PostgreSQL...")
        try:
            version = await conn.fetchval("SELECT version()")
            print(f"Версия PostgreSQL: {version.split(',')[0]}")
            
            # Дополнительные проверки
            print("\nДополнительные проверки:")
            print(f"- Количество соединений: {await conn.fetchval('SELECT count(*) FROM pg_stat_activity')}")
            print(f"- Размер БД: {await conn.fetchval('SELECT pg_size_pretty(pg_database_size($1))', db_name)}")
        except Exception as e:
            print(f"[ERROR] Ошибка выполнения запроса: {e}")

        # Шаг 5: Закрытие соединения
        print("\n[5/5] Закрытие соединения...")
        try:
            await conn.close()
            print("[OK] Соединение закрыто корректно")
        except Exception as e:
            print(f"[ERROR] Ошибка при закрытии соединения: {e}")

    except Exception as e:
        print(f"\n[ERROR] Критическая ошибка: {type(e).__name__}: {e}")
    finally:
        print(f"\n=== Тестирование завершено ===")
        print(f"Время окончания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(test_database())
