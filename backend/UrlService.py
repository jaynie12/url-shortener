from datetime import datetime

from fastapi import HTTPException, Request
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
            return RedirectResponse(url=cached_url, status_code=302)

        # If not in cache, check database
        url_data = await self.db.get("urls", short_code, "short_code", pool)
        if url_data is None:
            raise HTTPException(
                status_code=404,
                detail="Short code not found"
            )

        # Cache the result for future requests
        await self.cache.set_string(short_code, 600, url_data["long_url"], redis_client)

        #move into own function
        click_record = await self.db.insert_click_record({
            "url_id": await self.get_url_id_from_short_code(short_code, request),
            "referrer": request.headers.get("referer"),
            "country": request.headers.get("country"),
            "user_agent": request.headers.get("user-agent"),
            "clicked_at": datetime.now()
        }, pool)
        print(f"Click record created: {click_record}")

        return RedirectResponse(url=url_data["long_url"], status_code=302) #Permanent Page Moves

    async def get_click_count(self, short_code: str, request: Request):
        pool = self.get_pool(request)
        click_count = await self.db.get_click_count(short_code, pool)
        return {"short_code": short_code, "click_count": click_count}

    async def delete_short_code(self, table: str, value: str, column: str, request: Request):
        pool = self.get_pool(request)
        redis_client = self.get_redis_client(request)
        await self.db.delete(table, value, column, pool)
        await self.cache.delete(value, redis_client)
        return {"message": "Short code deleted"}

    async def update_short_code(self, table: str, value: str, column: str, data: dict, request: Request):
        pool = self.get_pool(request)
        redis_client = self.get_redis_client(request)
        await self.db.update(table, value, column, data, pool)
        await self.cache.update_string(value, 600, data["long_url"], redis_client)
        return {"message": "Short code updated"}

    async def get_url_id_from_short_code(self, short_code: str, request: Request):
        pool = self.get_pool(request)
        url_data = await self.db.get("urls", short_code, "short_code", pool)
        if url_data is None:
            raise HTTPException(
                status_code=404,
                detail="Short code not found"
            )
        return url_data["id"]
