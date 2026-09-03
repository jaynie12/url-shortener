import os
import redis
from psycopg2 import pool as pg_pool_module

def pg_connection():
    pg_pool = pg_pool_module.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    port=5432,
    dbname="url-shortener",
    user="postgres",
    password=os.getenv("PG_PASSWORD"),
    )
    return pg_pool

def redis_connection():
    redis_host = 'localhost'
    redis_port = 6379
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    return redis_client