import logging

from src.app_config import (
    AppConfig,
    PostgresConfig,
    SecretsConfig,
)

logger: logging.Logger = logging.getLogger(__name__)


def create_app_config() -> AppConfig:
    return AppConfig(
        postgres=PostgresConfig(),
        secret=SecretsConfig(),
    )
