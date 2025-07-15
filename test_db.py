import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

async def test_database():
    try:
        # Подключение к базе данных
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres", 
            password="Rerfhtre1964hfpf",  # Замените на ваш пароль
            database="sro_chatbot"
        )
        
        print("✅ Подключение к базе данных успешно!")
        
        # Простой тест
        result = await conn.fetchval("SELECT version()")
        print(f"Версия PostgreSQL: {result}")
        
        # Закрытие соединения
        await conn.close()
        print("✅ Соединение закрыто")
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    asyncio.run(test_database())
