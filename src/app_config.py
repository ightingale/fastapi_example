from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


class BotConfig(BaseSettings, env_prefix="BOT_"):
    token: SecretStr
    channel_id: int
    notifications_topic_id: int
    new_users_topic_id: int


class SecretsConfig(BaseSettings, env_prefix="SECRETS_"):
    jwt: SecretStr
    manager: SecretStr

    admin_user: str
    admin_password: SecretStr
    admin_jwt: SecretStr


class FKPaymentConfig(BaseSettings, env_prefix="FKPAYMENT_"):
    secret_key: str
    shop_id: int


class UPPaymentConfig(BaseSettings, env_prefix="UPPAYMENT_"):
    secret_key: str
    public_key: str


class YKPaymentConfig(BaseSettings, env_prefix="YKPAYMENT_"):
    secret_key: SecretStr
    shop_id: int


class PostgresConfig(BaseSettings, env_prefix="POSTGRES_"):
    host: str
    db: str
    password: SecretStr
    port: int
    user: str

    def build_dsn(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        )


class TeleParserConfig(BaseSettings, env_prefix="TELEPARSER_"):
    redis_host: str
    redis_port: int
    broker_db: int
    result_db: int
    session_data_db: int
    data_db: int

    @property
    def broker_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.broker_db}"

    @property
    def result_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.result_db}"

    @property
    def data_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.data_db}"


class S3StorageConfig(BaseSettings, env_prefix="S3Storage_"):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str

    @property
    def url(self) -> str:
        return f"http://{self.endpoint_url}"


class CommonConfig(BaseSettings, env_prefix="COMMON_"):
    max_numbers_per_check: int


class AppConfig(BaseModel):
    common: CommonConfig
    bot: BotConfig
    teleparser: TeleParserConfig
    postgres: PostgresConfig
    up_payment: UPPaymentConfig
    fk_payment: FKPaymentConfig
    yk_payment: YKPaymentConfig
    secret: SecretsConfig
    s3storage: S3StorageConfig
