from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app_config import AppConfig
from src.factory.app_config import create_app_config


class MainProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_config(self) -> AppConfig:
        return create_app_config()


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
