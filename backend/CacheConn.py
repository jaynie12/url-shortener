import asyncio

class RedisCache:
    async def get(self, cache_key,  redis_client):
        return await redis_client.get(cache_key)

    async def delete(self, cache_key, redis_client):
        await redis_client.delete(cache_key)

    async def set_string(self, cache_key: str, ttl: int, value: str,redis_client):
        await redis_client.set(cache_key, value, ex=ttl)

    async def update_string(self, cache_key: str, ttl: int, value: str, redis_client):
        await redis_client.set(cache_key, value, ex=ttl)
