import enum
from datetime import timedelta, datetime, UTC

from sqlalchemy import String, Enum, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, MappedColumn, relationship

from .user import User
from ..setup import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = MappedColumn(primary_key=True, unique=True, )
    user_id: Mapped[int] = MappedColumn(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = MappedColumn(unique=True, index=True)
    is_revoked: Mapped[bool] = MappedColumn(default=False)
    expire_at: Mapped[DateTime] = MappedColumn(TIMESTAMP(True),nullable=False)
    create_at: Mapped[DateTime] = MappedColumn(TIMESTAMP(True), server_default=func.now())
    update_at: Mapped[DateTime] = MappedColumn(TIMESTAMP(True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")

