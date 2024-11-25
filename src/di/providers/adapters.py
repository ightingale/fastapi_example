from typing import AsyncIterable

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dishka import Provider, Scope, provide
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.data_access.models.user import UserDb
from src.dependencies.auth.depend import UserManager
from src.app_config import AppConfig, FKPaymentConfig, UPPaymentConfig
from src.factory.app_config import create_app_config


class MainProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_config(self) -> AppConfig:
        return create_app_config()

    @provide
    async def get_fk_config(self, config: AppConfig) -> FKPaymentConfig:
        return config.fk_payment

    @provide
    async def get_up_config(self, config: AppConfig) -> UPPaymentConfig:
        return config.up_payment

    @provide
    async def get_bot(self, config: AppConfig) -> AsyncIterable[Bot]:
        bot = Bot(
            token=config.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        try:
            yield bot
        finally:
            await bot.session.close()


class SqlalchemyProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self, config: AppConfig) -> AsyncEngine:
        # PostgreSQL Максимум соединений по умолчанию - 100
        #  с данными настройками 4 воркера займут 40 соединений
        return create_async_engine(
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

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session


class FastapiUsersProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_jwt_strategy(self, config: AppConfig) -> JWTStrategy:
        return JWTStrategy(secret=config.secret.jwt, lifetime_seconds=3600 * 72)

    @provide(scope=Scope.APP)
    def provide_auth_backend(self, jwt_strategy: JWTStrategy) -> AuthenticationBackend:
        cookie_transport = CookieTransport(
            cookie_name="smartfit", cookie_max_age=3600 * 72
        )

        auth_backend = AuthenticationBackend(
            name="jwt",
            transport=cookie_transport,
            get_strategy=lambda: jwt_strategy,
        )

        return auth_backend

    @provide(scope=Scope.REQUEST)
    def provide_user_manager(
        self,
        config: AppConfig,
        session: AsyncSession,
    ) -> UserManager:
        user_db = SQLAlchemyUserDatabase(session, UserDb)  # type: ignore
        user_manager = UserManager(
            reset_password_token_secret=config.secret.jwt.get_secret_value(),
            verification_token_secret=config.secret.manager.get_secret_value(),
            user_db=user_db,
        )
        return user_manager
