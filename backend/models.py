from pydantic import BaseModel
from datetime import datetime

class CreateUrlRequest(BaseModel):
    short_code: str
    long_url: str
    user_id: str
    created_at: datetime | None = None
    expired_at: datetime | None = None

class CreateClickRecordRequest(BaseModel):
    url_id: int
    clicked_at: datetime | None = None
    referrer: str | None = None
    country: str | None = None
    user_agent: str | None = None

class UpdateUrlRequest(BaseModel):
    long_url: str | None = None
    expired_at: datetime | None = None