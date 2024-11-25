from typing import AsyncIterable

import aioboto3
import aiohttp
from aiogram import Bot
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.presentation.interactors.billing import (
    PaymentInteractor,
    TariffInteractor,
)
from src.presentation.interactors.holder import HolderInteractor
from src.presentation.services.payment import (
    FKPayment,
    UnitPayPayment,
    YooKassaPayment,
)
from src.presentation.services.task import TaskController
from src.app_config import AppConfig
from src.presentation.interactors.bot import (
    NewUserNotifier,
    BalanceTopUpNotifier,
    AdminAuthNotifier,
)
from src.presentation.interactors.notifications import NotificationsGateWay
from src.presentation.interactors.task import TaskGateWay
from src.presentation.services.s3 import S3StorageInteractor
from src.presentation.interactors.history import TaskHistoryGateWay


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def result_backend(self, config: AppConfig) -> RedisAsyncResultBackend:
        return RedisAsyncResultBackend(redis_url=config.teleparser.result_url)

    @provide(scope=Scope.APP)
    async def broker(
        self, config: AppConfig, result_backend: RedisAsyncResultBackend
    ) -> ListQueueBroker:
        return ListQueueBroker(url=config.teleparser.broker_url).with_result_backend(
            result_backend=result_backend
        )

    @provide
    async def provide_task_controller(self, broker: ListQueueBroker) -> TaskController:
        return TaskController(broker=broker)

    @provide(scope=Scope.APP)
    async def provide_fk_payment(self, config: AppConfig) -> FKPayment:
        return FKPayment(config=config.fk_payment)

    @provide(scope=Scope.APP)
    async def provide_up_payment(self, config: AppConfig) -> UnitPayPayment:
        return UnitPayPayment(config=config.up_payment)

    @provide(scope=Scope.APP)
    async def provide_yk_payment(
        self, config: AppConfig
    ) -> AsyncIterable[YooKassaPayment]:
        session = aiohttp.ClientSession()
        yield YooKassaPayment(config=config.yk_payment, session=session)
        await session.close()

    @provide
    async def get_payment_provider(self, session: AsyncSession) -> PaymentInteractor:
        return PaymentInteractor(session=session)

    @provide
    async def get_holder_provider(self, session: AsyncSession) -> HolderInteractor:
        return HolderInteractor(session=session)

    @provide
    async def get_tariffs_provider(self, session: AsyncSession) -> TariffInteractor:
        return TariffInteractor(session=session)

    @provide
    async def get_task_gateway(self, session: AsyncSession) -> TaskGateWay:
        return TaskGateWay(session=session)

    @provide
    async def get_notification_gateway(
        self, session: AsyncSession
    ) -> NotificationsGateWay:
        return NotificationsGateWay(session=session)

    @provide
    async def get_task_history_gateway(
        self, session: AsyncSession
    ) -> TaskHistoryGateWay:
        return TaskHistoryGateWay(session=session)

    @provide
    async def get_s3storage_client(
        self, config: AppConfig
    ) -> AsyncIterable[aioboto3.Session]:
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=config.s3storage.url,
            aws_access_key_id=config.s3storage.access_key,
            aws_secret_access_key=config.s3storage.secret_key,
        ) as s3_client:
            yield s3_client

    @provide
    async def get_s3_interactor(
        self, client: aioboto3.Session, config: AppConfig
    ) -> S3StorageInteractor:
        return S3StorageInteractor(
            client=client, bucket_name=config.s3storage.bucket_name
        )

    @provide
    async def get_notifier_new_user(
        self, bot: Bot, config: AppConfig
    ) -> NewUserNotifier:
        return NewUserNotifier(bot=bot, config=config.bot)

    @provide
    async def get_notifier_top_up(
        self, bot: Bot, config: AppConfig
    ) -> BalanceTopUpNotifier:
        return BalanceTopUpNotifier(bot=bot, config=config.bot)

    @provide(scope=Scope.APP)
    async def get_admin_auth_notifier(
        self, bot: Bot, config: AppConfig
    ) -> AdminAuthNotifier:
        return AdminAuthNotifier(bot=bot, config=config.bot)
