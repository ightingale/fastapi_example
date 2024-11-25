import logging

from dishka import AsyncContainer
from fastapi import Request
from jwt import PyJWTError
from sqladmin.authentication import AuthenticationBackend

from src.app_config import AppConfig
from src.utils.jwt import generate_jwt, decode_jwt

logger: logging.Logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        container: AsyncContainer = request.state.dishka_container
        config = await container.get(AppConfig)

        form = await request.form()
        username, password = form["username"], form["password"]
        if (
            username != config.secret.admin_user
            or password != config.secret.admin_password.get_secret_value()
        ):
            return False

        data = {"sub": "admin", "aud": ["sqladmin:auth"]}
        token = generate_jwt(data, config.secret.admin_jwt, 3600, algorithm="HS256")
        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        container: AsyncContainer = request.state.dishka_container
        config = await container.get(AppConfig)

        token = request.session.get("token")

        if not token:
            return False

        try:
            data = decode_jwt(
                token, config.secret.admin_jwt, ["sqladmin:auth"], algorithms=["HS256"]
            )
            if data.get("sub") != "admin":
                return False
        except PyJWTError:
            return False

        return True
