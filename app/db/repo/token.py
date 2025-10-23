from datetime import datetime, UTC, timedelta
from typing import Union

from sqlalchemy import Insert, Update, Select

from app.core.config import logger
from app.db.models.refresh_token import RefreshToken
from app.db.repo.base import BaseRepo
from sqlalchemy.exc import SQLAlchemyError


class Token(BaseRepo):

    async def save_refresh_token(self, user_id: int, refresh_token: str) -> Union[RefreshToken, None]:

        try:

            data = {
                "user_id": user_id,
                "token": refresh_token,
                "expire_at": datetime.now(UTC) + timedelta(days=7)
            }
            stmt = (
                Insert(RefreshToken)
                .values(**data)
                .returning(RefreshToken)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error while saving refresh token: {e}")
            raise Exception(f"Error while saving refresh token: {e}")

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error while saving refresh token: {e}")
            raise Exception(f"Error while saving refresh token: {e}")

    async def get_refresh_token(self, refresh_token: str) -> Union[RefreshToken, None]:
        try:
            stmt = (
                Select(RefreshToken)
                .where(RefreshToken.token == refresh_token)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.info(f"Error while getting refresh token: {e}")
            raise Exception(f"Error while getting refresh token: {e}")
        except Exception as e:
            logger.info(f"Error while getting refresh token: {e}")
            raise Exception(f"Error while getting refresh token: {e}")

    async def revoked_by_id(self, token_id: int) -> bool:

        try:
            stmt = (
                Update(RefreshToken)
                .where(RefreshToken.id == token_id)
                .values(is_revoked=True)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error while revoke refresh token by id: {e}")
            raise Exception(f"Error while revoke refresh token by id: {e}")

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error while revoke refresh token by id: {e}")
            raise Exception(f"Error while revoke refresh token by id: {e}")

    async def revoked_by_token(self, token: str) -> bool:

        try:
            stmt = (
                Update(RefreshToken)
                .where(RefreshToken.token == token)
                .values(is_revoked=True)
                .returning(RefreshToken.is_revoked)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            is_revoked = result.scalar_one_or_none()
            if is_revoked:
                logger.debug(f"✅ Refresh token by id={token} was revoked")
            else:
                logger.warning(f"⚠️ No refresh token found with id={token}")

            return is_revoked
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error while revoke refresh token by id: {e}")
            raise Exception(f"Error while revoke refresh token by id: {e}")

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error while revoke refresh token by id: {e}")
            raise Exception(f"Error while revoke refresh token by id: {e}")

    async def update_refresh_token_by_id(self, token_id: int, refresh_token: str) -> Union[RefreshToken, None]:

        try:
            expire_at = datetime.now(UTC) + timedelta(days=7)
            stmt = (
                Update(RefreshToken)
                .where(RefreshToken.id == token_id)
                .values(token= refresh_token,expire_at=expire_at)
                .returning(RefreshToken)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_token = result.scalar_one_or_none()

            if updated_token:
                logger.info(f"✅ Refresh token updated for id={token_id}")
            else:
                logger.warning(f"⚠️ No refresh token found with id={token_id}")

            return updated_token
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error while update refresh token by id: {e}",exc_info=True)
            raise Exception(f"Error while update refresh token by id: {e}")

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error while update refresh token by id: {e}")
            raise Exception(f"Error while update refresh token by id: {e}")
