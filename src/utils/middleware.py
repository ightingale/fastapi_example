import logging


logger: logging.Logger = logging.getLogger(__name__)


async def validation_exception_handler(request, exc):
    logger.error(f"Validation error for request {request.url}: {exc.errors()}")
