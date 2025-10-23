from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repo.token import Token
from app.db.repo.user import UserRepo


@dataclass
class RequestRepo:
    session: AsyncSession

    @property
    def user(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def token(self) -> Token:
        return Token(self.session)
