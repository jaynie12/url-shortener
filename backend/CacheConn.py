import asyncio

#https://redis.io/docs/latest/develop/use-cases/rate-limiter/redis-py/#fixed-window-counter   Redis management of rate limiting

SCRIPT = """
local key    = KEYS[1]
local limit  = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local count = redis.call('INCR', key)
if count == 1 then
    redis.call('EXPIRE', key, window)
end

local ttl = redis.call('PTTL', key)

if count > limit then
    return {0, ttl}
end
return {1, ttl}
"""
class RedisCache:
    async def get(self, cache_key,  redis_client):
        return await redis_client.get(cache_key)

    async def delete(self, cache_key, redis_client):
        await redis_client.delete(cache_key)

    async def set_string(self, cache_key: str, ttl: int, value: str,redis_client):
        await redis_client.set(cache_key, value, ex=ttl)

    async def update_string(self, cache_key: str, ttl: int, value: str, redis_client):
        await redis_client.set(cache_key, value, ex=ttl)

    def is_allowed(self, client, key: str, limit: int, window_seconds: int) -> dict:
        script = client.register_script(SCRIPT)
        allowed = script(keys=[key], args=[limit, window_seconds], client=client)
        return {"allowed": bool(allowed)}

#Jaynie note
#INCR creates a new key with value 1 if it doesn't exist, and sets the expiration time to the specified window.
# # If the key already exists, it increments the value by 1 and returns the current count.
# # If the count exceeds the limit, it returns 0 (not allowed) along with the remaining time to live (TTL) for the key. 
# #Otherwise, it returns 1 (allowed) and a TTL of 0.
