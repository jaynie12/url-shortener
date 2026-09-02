import databaseUtils
import redis
from cache import RedisCache

#HGETALL Returns all fields and values of the hash stored at key

def get_long_url(short_code:str):
    cache_key=f"short_code:{short_code}"
    cached = redis.get(cache_key)
    if cached:
        ##test
        pass