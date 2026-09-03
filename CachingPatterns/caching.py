import redis
import connections

def get_redis_data(cache_key):
    redis_client=connections.redis_connection()
    redis_client.get(cache_key)

def delete_redis_data(cache_key):
    redis_client=connections.redis_connection()
    redis_client.delete(cache_key)

def set_redis_data_string(cache_key:str, ttl:int, value: str):
    redis_client=connections.redis_connection()
    redis_client.set(cache_key,ttl,value)




