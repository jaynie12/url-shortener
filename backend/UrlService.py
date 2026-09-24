from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from db import PostgresCRUD as db
from CacheConn import RedisCache as cache

class UrlService:
    def __init__(self):
        self.db = db()
        self.cache = cache()

    def get_pool(self, request: Request):
        return request.app.state.pool

    def get_redis_client(self, request: Request):
        return request.app.state.redis_client

    async def create_url(self, short_code: str, long_url: str, request: Request):
        # Check that short_code is not already in use
        pool = self.get_pool(request)
        existing_url = await self.db.get("urls", short_code, "short_code", pool)
        if existing_url:
            raise HTTPException(
                status_code=400,
                detail="Short code already in use"
            )
        await self.db.create({"short_code": short_code, "long_url": long_url}, pool)

    async def get_url(self, short_code: str, request:Request):
        # Check cache first
        pool =  self.get_pool(request)
        redis_client = self.get_redis_client(request)
        cached_url = await self.cache.get(short_code, redis_client)
        if cached_url:
            return cached_url

        # If not in cache, check database
        url_data = await self.db.get("urls", short_code, "short_code", pool)
        if url_data is None:
            raise HTTPException(
                status_code=404,
                detail="Short code not found"
            )

        # Cache the result for future requests
        await self.cache.set_string(short_code, 60, url_data["long_url"], redis_client)
        return RedirectResponse(url=url_data["long_url"], status_code=302) #Permanent Page Moves

    async def get_click_count(self, short_code: str, request: Request):
        pool = self.get_pool(request)
        click_count = await self.db.get_click_count(short_code, pool)
        return {"short_code": short_code, "click_count": click_count}