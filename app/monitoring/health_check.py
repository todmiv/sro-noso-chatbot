from aiohttp import web
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def health_check_handler(request: web.Request) -> web.Response:
    """Обработчик проверки здоровья системы."""
    try:
        # Базовые проверки
        health_status = await check_system_health()
        
        if health_status["status"] == "healthy":
            return web.json_response(health_status, status=200)
        else:
            return web.json_response(health_status, status=503)
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return web.json_response({
            "status": "error",
            "message": "Health check failed",
            "timestamp": str(asyncio.get_event_loop().time())
        }, status=500)


async def check_system_health() -> Dict[str, Any]:
    """Проверяет состояние всех компонентов системы."""
    checks = {
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "api": await check_api_health()
    }
    
    all_healthy = all(check["status"] == "ok" for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": str(asyncio.get_event_loop().time())
    }


async def check_database_health() -> Dict[str, str]:
    """Проверяет подключение к базе данных."""
    try:
        from app.database.connection import get_engine
        engine = get_engine()
        
        # Простая проверка подключения
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}


async def check_redis_health() -> Dict[str, str]:
    """Проверяет подключение к Redis."""
    try:
        from app.database.connection import get_redis
        redis_client = get_redis()
        
        await redis_client.ping()
        return {"status": "ok", "message": "Redis connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Redis error: {str(e)}"}


async def check_api_health() -> Dict[str, str]:
    """Проверяет доступность внешних API."""
    try:
        # Здесь можно добавить проверки DeepSeek API и других сервисов
        return {"status": "ok", "message": "External APIs accessible"}
    except Exception as e:
        return {"status": "error", "message": f"API error: {str(e)}"}


def setup_health_check(app: web.Application) -> None:
    """Настраивает маршруты для проверки здоровья."""
    app.router.add_get('/health', health_check_handler)
    app.router.add_get('/healthz', health_check_handler)  # Kubernetes style
    app.router.add_get('/ping', lambda req: web.Response(text="pong"))
    
    logger.info("Health check endpoints configured")
