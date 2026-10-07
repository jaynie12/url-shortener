
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import PlainTextResponse
from backend.CacheConn import RedisCache as cache
from starlette.responses import Response

class Middleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.cache = cache()

    async def log_request(self, request: Request):
        # Log the request details (method, URL, headers, etc.)
        print(f"Request: {request.method} {request.url}")
        print(f"Headers: {request.headers}")

    async def dispatch(self, request: Request, call_next):
        redis_client = request.app.state.redis_client
        ip_address_key = f"ip:{request.client.host}"
        limiter = await self.cache.is_allowed(redis_client, ip_address_key, 10, 60)  # 10 requests per minute
        if limiter["allowed"]:
            response = await call_next(request)
            return response
        else:
            return PlainTextResponse(
                "Too many requests. Please try again later.",
                status_code=429
            )