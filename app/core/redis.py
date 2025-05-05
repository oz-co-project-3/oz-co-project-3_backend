from redis.asyncio import Redis

from app.core.settings import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
