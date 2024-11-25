import logging

from dishka.integrations.fastapi import FromDishka, setup_dishka
from fastapi import FastAPI, APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.middleware.cors import CORSMiddleware

from src.dependencies.admin.auth import AdminAuth
from src.dependencies.admin.models import (
    TariffAdmin,
    PaymentAdmin,
    TaskDBAdmin,
    UserAdmin,
)
from src.dependencies.auth.depend import (
    auth_backend,
    fastapi_users,
)
from src.factory.app_config import create_app_config
from src.factory.container import container_factory
from src.presentation.web_api.routers.billing import billing_router
from src.presentation.web_api.routers.task import task_router
from src.presentation.web_api.routers.user import user_router
from src.presentation.web_api.schemas.fastapi_users import (
    UserCreate,
    UserRead,
)
from src.utils.loggers import setup_logger
from src.utils.middleware import (
    validation_exception_handler, )

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

    admin.add_view(UserAdmin)
    admin.add_view(TariffAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(TaskDBAdmin)


def init_di(app: FastAPI) -> None:
    setup_dishka(container_factory(), app)


def init_routers(app: FastAPI) -> None:
    app.include_router(
        fastapi_users.get_auth_router(FromDishka[auth_backend]),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )

    api_router = APIRouter(prefix="/api")

    app.include_router(task_router)
    app.include_router(billing_router)
    app.include_router(api_router)
    app.include_router(user_router)

    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],  # Разрешаем все методы
        allow_headers=["*"],  # Разрешаем любые заголовки
    )
    app.add_exception_handler(RequestValidationError, validation_exception_handler)


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API",
        version="1.0.0",
        description="API",
        routes=app.routes,
    )

    # Добавляем версию OpenAPI
    openapi_schema["openapi"] = "3.0.0"  # или используйте нужную вам версию

    openapi_schema["paths"]["/task_ws"] = {
        "get": {
            "summary": "WebSocket для мониторинга прогресса",
            "description": (
                "WebSocket соединение для отслеживания прогресса задачи с `task_id`. "
                "Используется для отправки промежуточных статусов выполнения.\n\n"
                "### Пример возвращаемого JSON:\n"
                "```json\n"
                "{\n"
                '  "progress": 0,\n'
                "}\n"
                "```"
            ),
            "parameters": [
                {
                    "name": "task_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "Идентификатор задачи",
                }
            ],
            "responses": {
                "101": {
                    "description": "Switching Protocols - успешное установление WebSocket соединения",
                },
                "400": {
                    "description": "Bad Request - ошибка запроса",
                },
            },
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app() -> FastAPI:
    setup_logger()
    app = FastAPI()

    init_di(app)
    init_routers(app)
    init_admin(app)

    app.openapi = lambda: custom_openapi(app)
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
