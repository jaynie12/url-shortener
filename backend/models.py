from pydantic import BaseModel


class CreateUrlRequest(BaseModel):
    short_code: str
    long_url: str
    user_id: str