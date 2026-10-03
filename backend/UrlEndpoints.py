from fastapi import APIRouter, Request,Depends
from UrlService import UrlService
from models import CreateUrlRequest, CreateClickRecordRequest, UpdateUrlRequest

router = APIRouter()
## TEMP calling service here  - probably best to make it a getter/setter
service = UrlService()

@router.post("/create-url")
async def create_url(
    data: CreateUrlRequest,
    request: Request
):
    return await service.create_url(
        data.short_code,
        data.long_url,
        request
    )
@router.get("/{short_code}")
async def get_url(short_code: str, request: Request):
    long_url = await service.get_url(short_code,request)
    print(f"Redirecting to: {long_url}")
    return long_url

@router.get("/urls/{short_code}/stats")
async def get_url_stats(short_code: str, request: Request):
    click_count = await service.get_click_count(short_code,request)
    return {"click_count": click_count["click_count"]}

@router.delete("/urls/{short_code}")
async def delete_url(short_code: str, request: Request):
    await service.delete_short_code("urls", short_code, "short_code", request)
    return {"message": "URL deleted"}

@router.patch("/urls/{short_code}")
async def update_url(short_code: str, data: UpdateUrlRequest, request: Request):
    await service.update_short_code("urls", short_code, "short_code", data, request)
    return {"message": "URL updated"}