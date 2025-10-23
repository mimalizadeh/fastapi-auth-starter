from typing import Union

from asyncpg import UniqueViolationError
from sqlalchemy import Insert, select, or_
from sqlalchemy.dialects.postgresql import asyncpg

from app.core.config import logger
from app.db.models.user import User, Role
from app.db.repo.base import BaseRepo
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.user import UserSchemaIn
from app.core.security import hash_password


class UserRepo(BaseRepo):

    async def create(self, user: UserSchemaIn):
        try:
            data = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": Role.USER,
                "hashed_password": hash_password(user.password),
            }
            stmt = (
                Insert(User)
                .values(**data)
                .returning(User)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create user {user.username}: {e}")
            raise Exception(f"Failed to create user {user.username}: {e}")
        except UniqueViolationError as e:
            logger.error(f"unique error {user.username}: {e}")
            raise Exception(f"Failed to create user {user.username}: {e}")
        except Exception as e:
            logger.error(f"Failed to create user {user.username}: {e}")
            raise Exception(f"Failed to create user {user.username}: {e}")

    async def get_by_email(self, email: str) -> Union[User, None]:
        try:
            stmt = (
                select(User)
                .where(User.email == email)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"database error when getting user by email: {e}")
            raise e
        except Exception as e:
            logger.error(f"database error when getting user by email: {e}")
            raise e

    async def get_by_username(self, username: str) -> Union[User, None]:
        try:
            stmt = (
                select(User)
                .where(User.username == username)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"database error when getting user by username: {e}")
            raise e
        except Exception as e:
            logger.error(f"database error when getting user by username: {e}")
            raise e

    async def get_by_email_or_username(self, username: str, email: str) -> Union[User, None]:
        try:
            stmt = (
                select(User)
                .where(or_(User.username == username, User.email == email))
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"database error when getting user by username: {e}")
            raise e
        except Exception as e:
            logger.error(f"database error when getting user by username: {e}")
            raise e

    async def get_by_id(self, user_id: int) -> Union[User, None]:

        try:
            stmt = (
                select(User)
                .where(User.id == user_id)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"database error when getting user by id: {e}")
            raise e
        except Exception as e:
            logger.error(f"database error when getting user by id: {e}")
            raise e
