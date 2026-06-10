import redis.asyncio as aioredis
from settings import settings

# Global redis client
redis_client = None

async def init_redis():
    """Initializes the Redis connection."""
    global redis_client
    redis_client = await aioredis.from_url(
        settings.REDIS_URL,
        password=settings.REDIS_PASSWORD or None,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    """Closes the Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_redis():
    """Dependency to get the Redis client."""
    return redis_client
