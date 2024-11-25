import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Sequence

import jwt
from pydantic.types import SecretType, SecretStr

logger: logging.Logger = logging.getLogger(__name__)

JWT_ALGORITHM = "HS256"


def _get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: dict,
    secret: SecretType,
    lifetime_seconds: int | None = None,
    algorithm: str = JWT_ALGORITHM,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.now(timezone.utc) + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str,
    secret: SecretType,
    audience: list[str],
    algorithms: Sequence[str] = (JWT_ALGORITHM,),
) -> dict[str, Any]:
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
