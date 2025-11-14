from time import timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from jose import JWTError, ExpiredSignatureError
from app.core.config import logger
from app.core.security import decode_token
from app.db.models.user import User
from app.dependencies.repo import RepoRequestDep
from app.services.auth_service import auth_service
from app.services.auth_service import oauth2_scheme
from datetime import datetime,timezone

async def get_current_user(repo: RepoRequestDep,
                           token: str = Depends(oauth2_scheme)
                           ) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_token(token=token)
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            print("user is none")
            raise credentials_exception
        user = await repo.user.get_by_id(user_id=user_id)
        if not user:
            print("not found user")
            raise credentials_exception
        return user
    except ExpiredSignatureError:
        raise credentials_exception
    except JWTError:
        raise credentials_exception
    except Exception as error:
        logger.error(f"Error decoding access token: {error}")
        raise credentials_exception


CurrentUserDep = Annotated[User, Depends(get_current_user)]
