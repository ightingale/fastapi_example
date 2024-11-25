from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, String, Float, ForeignKey, func
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data_access.models.types.int_pk import intpk
from src.presentation.entities import NotificationsType
from src.presentation.web_api.schemas.user import NotificationDTO
from .base import BaseDb


class UserDb(SQLAlchemyBaseUserTable[int], BaseDb):
    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0, nullable=False)


class Notification(BaseDb):
    __tablename__ = "notifications"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    type: Mapped[Enum] = mapped_column(SQLAEnum(NotificationsType))
    is_processed: Mapped[bool] = mapped_column(default=False)
    headline: Mapped[str]
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[Optional[UserDb]] = relationship(
        "UserDb", primaryjoin="Notification.user_id == UserDb.id"
    )

    def dto(self) -> NotificationDTO:
        return NotificationDTO(
            headline=self.headline, text=self.text, created_at=self.created_at
        )
