import os

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(
        URL.create(
            drivername="postgresql+asyncpg",
            username="postgres",
            password=os.getenv("PG_PASSWORD"),
            host="localhost",
            port=5432,
            database="url-shortener",
        ),
        pool_size=5,
        max_overflow=25,
    )

    app.state.pool = engine
    app.state.redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    yield

    await app.state.pool.dispose()
    await app.state.redis_client.close()
