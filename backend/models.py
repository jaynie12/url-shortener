from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class CreateUrlRequest(BaseModel):
    short_code: str
    long_url: str
    user_id: str

class CreateClickRecordRequest(BaseModel):
    url_id: int
    clicked_at: datetime | None = None
    referrer: str | None = None
    country: str | None = None
    user_agent: str | None = None

class UpdateUrlRequest(BaseModel):
    long_url: str

class DeleteUrlRequest(BaseModel):
    short_code: str

class UrlStatsResponse(BaseModel):
    short_code: str
    click_count: int
    