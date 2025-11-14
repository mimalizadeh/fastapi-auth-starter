from app.dependencies.user import CurrentUserDep
from fastapi import APIRouter

from app.schemas.user import UserSchema

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/me",response_model= UserSchema)
async def user_details(user: CurrentUserDep):
    """
    Check if user is authenticated return user data
    :param user: Current user
    :return: user data
    """
    return user
