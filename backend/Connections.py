import os

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import redis.asyncio as redis
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.pool = create_async_engine(
        URL.create(
            drivername="postgresql+asyncpg",
            username="postgres",
            host="localhost",
            port=5432,
            database="url-shortener",
        password=os.getenv("PG_PASSWORD"),
        ),
        pool_size=5,
        max_overflow=15,
        connect_args={"timeout": 60},
    )

    app.state.redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    yield

    await app.state.pool.dispose()
    await app.state.redis_client.close()