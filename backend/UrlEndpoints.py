from db import PostgresCRUD as db
from fastapi import APIRouter
from UrlService import UrlService as service

router = APIRouter()


class UrlEndpoints:
    def __init__(self):
        self.pg = db()
        self.service = service()
        
        #post create short code
    @router.post("/urls")
    def create_url(self, short_code: str, long_url: str):
        return self.service.create_url(short_code, long_url)
  
    @router.get("/{short_code}")
    def get_url(self, short_code: str):
        long_url = self.service.get_url(short_code)
        return long_url

    @router.get(" /urls/{code}/stats")
    def get_url_stats(self, code: str):
        long_url = self.service.get_url_stats(code)
        return long_url