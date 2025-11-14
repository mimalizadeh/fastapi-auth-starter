from typing import Annotated
from fastapi import HTTPException, Cookie
from fastapi import APIRouter, Response, Depends, status , Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import logger
from app.dependencies.repo import RepoRequestDep
from app.schemas.auth import TokenSchema, LoginSchema
from app.schemas.user import UserSchema, UserSchemaIn
from app.services.auth_service import auth_service
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signin", response_model=TokenSchema)
async def signin(response: Response,
                 repo: RepoRequestDep,
                 form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Sign in with an existing user
    """
    user = await auth_service.authenticate_user(repo=repo, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token_schema = await auth_service.create_token(user=user)

    # Save refresh schema
    await repo.token.save_refresh_token(user_id=user.id, refresh_token=token_schema.refresh_token)

    # set cookies
    response.set_cookie(key="access_token", value=token_schema.access_token, httponly=True, secure=True)
    response.set_cookie(key="refresh_token", value=token_schema.refresh_token, httponly=True, secure=True)

    return token_schema


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserSchemaIn, repo: RepoRequestDep):
    """
    Create a new user
    """
    existing_user = await repo.user.get_by_email_or_username(user.username, user.email)
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=409, detail="Email already registered")

        if existing_user.username == user.username:
            raise HTTPException(status_code=409, detail="Username already registered")

    user = await repo.user.create(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="There was an issue with your credentials")
    logger.info(f"New user registered: {user.email}")
    return user


@router.post("/refresh")
async def refresh_token(response: Response,
                        request: Request,
                        repo: RepoRequestDep):
    """
    Refresh the access token
    """
    refresh_token = request.cookies.get("refresh_token")
    new_tokens = await auth_service.refresh_token_update(repo=repo, refresh_token=refresh_token, response=response)
    return new_tokens


@router.post("/logout")
async def logout(response: Response,
                 repo: RepoRequestDep,
                 request: Request
                 ):
    """
    Logout the user
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    await repo.token.revoked_by_token(refresh_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
