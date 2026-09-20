import os
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
import redis.asyncio as redis
import asyncpg

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.pool = await asyncpg.create_pool(
        min_size=5,
        max_size=30,
        host="localhost",
        port=5432,
        database="url-shortener",
        user="postgres",
        password=os.getenv("PG_PASSWORD"),
    )

    app.state.redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    yield

    await app.state.pool.close()
    await app.state.redis_client.close()