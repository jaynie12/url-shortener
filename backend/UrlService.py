from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from db import PostgresCRUD as db
from CacheConn import RedisCache as cache

class UrlService:
    def __init__(self):
        self.pg = db()
        self.cache = cache()

    def create_url(self, short_code: str, long_url: str):
        # Check that short_code is not already in use
        existing_url = self.pg.get("urls", short_code, "short_code")
        if existing_url:
            raise HTTPException(
                status_code=400,
                detail="Short code already in use"
            )
        self.pg.create({"short_code": short_code, "long_url": long_url})

    def get_url(self, short_code: str):
        # Check cache first
        cached_url = self.cache.get(short_code)
        if cached_url:
            return cached_url.decode("utf-8")

        # If not in cache, check database
        url_data = self.pg.get("urls", short_code, "short_code")
        if url_data is None:
            raise HTTPException(
                status_code=404,
                detail="Short code not found"
            )

        # Cache the result for future requests
        self.cache.set_string(short_code, 60, url_data["long_url"])
        return RedirectResponse(url=url_data["long_url"], status_code=301) #Permanent Page Moves
