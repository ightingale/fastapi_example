from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


class SecretsConfig(BaseSettings, env_prefix="SECRET_"):
    admin_user: str
    admin_password: SecretStr
    admin_jwt: SecretStr


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


class AppConfig(BaseModel):
    postgres: PostgresConfig
    secrets: SecretsConfig
