from datetime import datetime
import json
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from db import PostgresCRUD as db
from CacheConn import RedisCache as cache
import logging
from sqlalchemy.exc import IntegrityError

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
        created_at = datetime.now()
        expired_at  = created_at.replace(year=created_at.year + 1)  # Set expiration to 1 year from now
        
        existing_url = await self.db.get("urls", short_code, "short_code", pool)
        if existing_url:
            raise HTTPException(
                status_code=409,
                detail="Short code already in use"
            )
        try:
            create_url = await self.db.create({"short_code": short_code, "long_url": long_url, "created_at": created_at, "expired_at": expired_at}, pool)
            if create_url:
                return {  "message": "Short code created successfully"}

        except Exception as error:
            raise HTTPException(
                status_code=409,
                detail="Short code already in use"
            ) from error

    async def get_url(self, short_code: str, request:Request) -> RedirectResponse:
        # Check cache first
        pool =  self.get_pool(request)
        redis_client = self.get_redis_client(request)
        cached_url = await self.cache.get(short_code, redis_client)
        print(f"Cached URL: {cached_url}")
        if cached_url:
            await self.insert_click_record(int(cached_url["id"]), request)
            return RedirectResponse(url=cached_url["long_url"], status_code=302)

        # If not in cache, check database
        url_data = await self.db.get("urls", short_code, "short_code", pool)
        print(f"URL data from DB: {url_data}")
        url_id = url_data["id"];
        if url_data is None:
            raise HTTPException(
                status_code=404,
                detail="Short code not found"
            )
        
        await self.insert_click_record(url_id, request)

        # Cache the result for future requests
        await self.cache.set_string(
                short_code,
                600,
                url_data,
                redis_client,
            )

        return RedirectResponse(url=url_data["long_url"], status_code=302) #Permanent Page Moves

    async def insert_click_record(self, url_id: int, request: Request):
        pool = self.get_pool(request)
        click_record = await self.db.insert_click_record({
            "url_id": url_id,
            "referrer": request.headers.get("referer"),
            "country": request.headers.get("country"),
            "user_agent": request.headers.get("user-agent"),
            "clicked_at": datetime.now()
        }, pool)
        
        return click_record

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
        await self.cache.update_string(value, 600, json.dumps(data, default=str), redis_client)
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
    