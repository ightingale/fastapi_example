from dishka import AsyncContainer, make_async_container

from src.di.providers.adapters import (
    SqlalchemyProvider,
    MainProvider,
)
from src.di.providers.usecases import UseCasesProvider


def container_factory() -> AsyncContainer:
    return make_async_container(
        MainProvider(), SqlalchemyProvider(), UseCasesProvider()
    )
