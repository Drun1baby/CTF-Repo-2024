import logging

from fastapi.responses import JSONResponse
from limits import RateLimitItemPerMinute
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter
from nicegui import app
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.types import ASGIApp

from . import admin as admin
from . import index as index
from . import static as static

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

        storage = MemoryStorage()
        self.moving_window = MovingWindowRateLimiter(storage)
        self.rate_limit = RateLimitItemPerMinute(60)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        match request.client:
            case (host, _) if (
                request.url.path.startswith("/_nicegui")
                or await self.moving_window.hit(self.rate_limit, host)
            ):
                return await call_next(request)
        logger.debug("Rate limit exceeded for %s, %r", request.client, self.rate_limit)
        return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)


app.add_middleware(RateLimitMiddleware)
