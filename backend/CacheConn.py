from Connections import ConnectionManager as connections


class RedisCache:
    def __init__(self):
        self.redis_client = connections.redis_connection()

    def get(self, cache_key):
        return self.redis_client.get(cache_key)

    def delete(self, cache_key):
        self.redis_client.delete(cache_key)

    def set_string(self, cache_key: str, ttl: int, value: str):
        self.redis_client.set(cache_key, value, ex=ttl)
