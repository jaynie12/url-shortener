import connections
import redis
from cache import RedisCache

#HGETALL Returns all fields and values of the hash stored at key

def get_long_url(short_code:str):
    cache_key=f"short_code:{short_code}"
    cached = redis.get(cache_key)
    if cached:
      return json.loads(cached)

    conn = connections.pg_connection().getconn()

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users WHERE id = %s;", (user_id,))
        row = cur.fetchone()
        if not row:
            return None
        user = {"id": row[0], "name": row[1], "email": row[2]}
        redis.setex(cache_key, 60, json.dumps(user))
        return user
    finally:
        connections.pg_connection().putconn(conn)