from redis.asyncio import Redis

redis = Redis(host="redis-dev", port=6379, decode_responses=True)
