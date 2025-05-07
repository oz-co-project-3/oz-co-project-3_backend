import redis.asyncio as aioredis

from app.core.settings import get_settings


def get_redis():
    settings = get_settings()
    return aioredis.Redis(
        host=settings.REDIS_HOST,
        port=int(settings.REDIS_PORT),
        decode_responses=True,
    )
