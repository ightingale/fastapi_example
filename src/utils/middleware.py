import logging

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger: logging.Logger = logging.getLogger(__name__)


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # logger.info(f"Query params: {request.query_params}")
        response = await call_next(request)
        # logger.info(f"Response headers: {response.headers}")
        if request.method == "POST":
            logger.info(f"Body: {request.body}")
        return response


async def validation_exception_handler(request, exc):
    logger.error(f"Validation error for request {request.url}: {exc.errors()}")
