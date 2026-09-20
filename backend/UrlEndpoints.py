from fastapi import APIRouter, Request,Depends
from UrlService import UrlService 

router = APIRouter()
## TEMP calling service here  - probably best to make it a getter/setter
service = UrlService()

@router.post("/urls")
async def create_url(short_code: str, long_url: str, request: Request):
    return await service.create_url(short_code, long_url,request)

@router.get("/{short_code}")
async def get_url(short_code: str, request: Request):
    long_url = await service.get_url(short_code,request)
    return long_url

@router.get(" /urls/{code}/stats")
async def get_url_stats( code: str, request: Request):
    stats = await service.get_url_stats(code,request)
    return stats