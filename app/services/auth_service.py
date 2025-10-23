from fastapi import HTTPException, status, Response, Request
from app.db.models.user import User
from app.core.security import verify_password, create_refresh_token, create_access_token
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import get_settings
from app.db.repo.request import RequestRepo
from app.core.config import logger
from app.schemas.auth import LoginSchema, TokenSchema

settings = get_settings()

class AuthService:
    """
    This service is responsible for handling authentication.

    """
    async def authenticate_user(self, repo: RequestRepo, email, password):
        user = await repo.user.get_by_email(email=email)
        if not user or not verify_password(plain_password=password, hashed_password=str(user.hashed_password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        return user

    async def create_token(self, user: User) -> TokenSchema:
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    async def refresh_token_update(self, refresh_token: str, repo: RequestRepo, response: Response) -> TokenSchema:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt_refresh_secret_key,
                algorithms=["HS256"],
            )
            user_id = int(payload.get("sub"))
        except ExpiredSignatureError:
            logger.warning("Refresh token expired")
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except JWTError:
            logger.warning("Invalid refresh token")
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        stored_refresh_token = await repo.token.get_refresh_token(refresh_token)
        if not stored_refresh_token or stored_refresh_token.is_revoked:
            logger.warning("Refresh token invalid or revoked")
            raise HTTPException(status_code=401, detail="Invalid or revoked token")

        user = await repo.user.get_by_id(user_id=user_id)
        if not user:
            logger.error(f"User not found for refresh token (user_id={user_id})")
            raise HTTPException(status_code=404, detail="User not found")

        # Generate new tokens
        token_schema = await self.create_token(user=user)

        await repo.token.update_refresh_token_by_id(int(stored_refresh_token.id),
                                                    refresh_token=token_schema.refresh_token)

        # Set cookies (HTTPS-aware)
        cookie_config = {
            "httponly": True,
            "secure": settings.is_production,  # False in local, True in production
            "samesite": "lax",
        }

        response.set_cookie(
            key="access_token",
            value=token_schema.access_token,
            max_age=15 * 60,  # 15 minutes
            **cookie_config,
        )
        response.set_cookie(
            key="refresh_token",
            value=token_schema.refresh_token,
            max_age=7 * 86400,  # 7 days
            **cookie_config,
        )

        logger.info(f"Refresh token renewed for user_id={user.id}")
        return token_schema

    async def extract_access_token(self, request: Request) -> TokenSchema:
        """Extract tokens from cookies safely."""
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if not access_token or not refresh_token:
            logger.debug("Access or refresh token missing from cookies")
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)


auth_service = AuthService()
