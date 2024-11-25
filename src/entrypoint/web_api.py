import logging

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, APIRouter, Request
from fastapi.exceptions import RequestValidationError
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine

from src.dependencies.admin.auth import AdminAuth
from src.factory.app_config import create_app_config
from src.factory.container import container_factory
from src.utils.loggers import setup_logger
from src.utils.middleware import (
    validation_exception_handler,
)

logger: logging.Logger = logging.getLogger(__name__)


def init_admin(app: FastAPI) -> None:
    config = create_app_config()
    engine = create_async_engine(
        config.postgres.build_dsn(),
        pool_size=10,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={
            "timeout": 15,
            "command_timeout": 5,
            "server_settings": {
                "jit": "off",
                "application_name": "web-api",
            },
        },
    )

    authentication_backend = AdminAuth(
        secret_key=config.secret.admin_jwt.get_secret_value()
    )
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(...)


def init_di(app: FastAPI) -> None:
    setup_dishka(container_factory(), app)


def init_routers(app: FastAPI) -> None:
    api_router = APIRouter(prefix="/api")
    api_router.include_router(...)

    app.add_exception_handler(RequestValidationError, validation_exception_handler)


def create_app() -> FastAPI:
    setup_logger()
    app = FastAPI()

    init_di(app)
    init_routers(app)
    init_admin(app)

    app.middleware("http")(log_requests)

    logger.info("Starting App...")
    return app


async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e
    return response
