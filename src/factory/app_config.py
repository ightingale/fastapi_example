import logging

from src.app_config import (
    AppConfig,
    TeleParserConfig,
    PostgresConfig,
    UPPaymentConfig,
    FKPaymentConfig,
    SecretsConfig,
    S3StorageConfig,
    BotConfig,
    YKPaymentConfig,
    CommonConfig,
)

logger: logging.Logger = logging.getLogger(__name__)


def create_app_config() -> AppConfig:
    return AppConfig(
        teleparser=TeleParserConfig(),
        postgres=PostgresConfig(),
        up_payment=UPPaymentConfig(),
        fk_payment=FKPaymentConfig(),
        yk_payment=YKPaymentConfig(),
        secret=SecretsConfig(),
        s3storage=S3StorageConfig(),
        bot=BotConfig(),
        common=CommonConfig(),
    )
