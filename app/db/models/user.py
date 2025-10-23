import enum

from sqlalchemy import String, Enum, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ..setup import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .refresh_token import RefreshToken


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = MappedColumn(primary_key=True)
    username: Mapped[str] = MappedColumn(index=True, unique=True)
    email: Mapped[str] = MappedColumn(unique=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[Enum] = MappedColumn(Enum(Role), default=Role.USER)

    create_at: Mapped[DateTime] = MappedColumn(TIMESTAMP(True), server_default=func.now())
    update_at: Mapped[DateTime] = MappedColumn(TIMESTAMP(True), server_default=func.now(), onupdate=func.now())

    refresh_tokens: Mapped["RefreshToken"] = relationship("RefreshToken", back_populates="user")
