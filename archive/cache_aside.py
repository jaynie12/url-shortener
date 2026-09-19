from db import PostgresCRUD
import connections
import logging
import json
logging.basicConfig(level=logging.INFO)


def cache_aside(short_code: str):
    db = PostgresCRUD()
    redis_client = connections.redis_connection()
    cached = redis_client.get(short_code)
    if cached:
        logging.info(f"Cached record: {short_code} found in Redis")
        return json.loads(cached)
    else:
        row = db.get("urls",short_code , "short_code")
        if row is None:
            return {}
        
    code = {'id': row[0], 'user_id': row[1], 'short_code': row[2], 'long_url':row[3]}
    redis_client.set(short_code, json.dumps(code),60)
    return code

if __name__ == '__main__':
    a = cache_aside("short0002")
    logging.info(a)