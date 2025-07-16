import asyncio
from app.database.connection import init_redis, get_redis, close_redis
from config.settings import config

async def test_redis_connection():
    try:
        print(f"Testing Redis connection to: {config.redis.url}")
        
        # Initialize Redis connection
        redis = await init_redis()
        
        # Test ping command
        pong = await redis.ping()
        print(f"Redis ping response: {pong}")
        
        # Test simple set/get
        await redis.set("test_key", "test_value")
        value = await redis.get("test_key")
        print(f"Redis get test value: {value}")
        
        return True
    except Exception as e:
        print(f"Redis connection failed: {str(e)}")
        return False
    finally:
        await close_redis()

if __name__ == "__main__":
    result = asyncio.run(test_redis_connection())
    print(f"Redis connection test {'passed' if result else 'failed'}")
