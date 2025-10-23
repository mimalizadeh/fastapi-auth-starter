from typing import Annotated
from fastapi import Depends, HTTPException, status, Cookie, Request, Response

from app.core.config import logger
from app.core.security import decode_token
from app.db.models.user import User
from app.dependencies.repo import RepoRequestDep
from app.services.auth_service import auth_service


async def get_current_user(request: Request, response: Response, repo: RepoRequestDep,
                           refresh_token: Annotated[str | None, Cookie()] = None,
                           access_token: Annotated[str | None, Cookie()] = None) -> User:
    """
    This dependence chek access token and refresh token for validation and authentication user.
     if access token is expired and refresh token is valid create new access token and refresh token and them as set cookie .

     :request: Request
     :response: Response
     :repo: Models repository
     :refresh_token: Refresh token
     :access_token: Access token
     :return: User Model
     """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        if access_token is None and refresh_token is None:
            try:
                logger.info("Extracting access token")
                token_schema = await auth_service.extract_access_token(request=request)
                access_token = token_schema.access_token
                refresh_token = token_schema.refresh_token
            except Exception as exc:
                logger.info(f"Failed to extract access token {exc}")
                raise credentials_exception

        if refresh_token is None:
            raise credentials_exception

        if access_token is None:
            tokens = await auth_service.refresh_token_update(refresh_token=refresh_token, repo=repo,
                                                             response=response)
            access_token = tokens.access_token

            logger.debug(f"Refreshed tokens: {tokens}")
            if access_token is None and refresh_token is None:
                raise credentials_exception

        payload = decode_token(access_token)
        logger.debug(f"payload: {payload}")
        user = payload.get("sub")
        if user is None:
            raise credentials_exception

        user = await repo.user.get_by_id(user_id=int(user))
        if user is None:
            logger.error(f"User {user} not found")
            raise credentials_exception
        return user

    except Exception as error:
        logger.error(f"Error decoding access token: {error}")
        raise credentials_exception


CurrentUserDep = Annotated[User, Depends(get_current_user)]
