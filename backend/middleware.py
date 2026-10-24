import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import PlainTextResponse
from CacheConn import RedisCache as cache

logger = logging.getLogger(__name__)


class Middleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.cache = cache()

    async def dispatch(self, request: Request, call_next):
        redis_client = request.app.state.redis_client
        ip_address_key = f"ip:{request.client.host}"
        limiter = await self.cache.is_allowed(redis_client, ip_address_key, 10, 60)  # 10 requests per minute
        if limiter["allowed"]:
            response = await call_next(request)
            return response
        else:
            logger.warning(
                "Request rate limited",
                extra={
                    "event": "request_rate_limited",
                    "method": request.method,
                    "path": request.url.path,
                },
            )
            return PlainTextResponse(
                "Too many requests. Please try again later.",
                status_code=429
            )