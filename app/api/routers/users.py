from typing import Annotated
from app.api.dependencies.auth import validate_is_authenticated
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep, get_current_user
from app.crud.user import change_password, create_user, get_user, get_user_by_email, get_user_by_username, get_users
from app.schemas.user import AuthUserSchema, ChangePasswordSchema, User, UserResponse, UserResponseRules, UserSchema
from fastapi import APIRouter, Depends, HTTPException
from app import models

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/id/{user_id}",
    response_model=UserResponseRules,
    dependencies=[Depends(validate_is_authenticated)],
)
async def user_details(
    user_id: int,
    db_session: DBSessionDep,
) -> UserResponseRules:
    """
    Get any user details
    """
    user = await get_user(db_session, user_id)
    return user


@router.get("/")
async def users(db_session: DBSessionDep) -> list[UserResponseRules]:
    users = await get_users(db_session)
    return users


@router.get("/me", dependencies=[Depends(validate_is_authenticated)], description='Required authentication')
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponseRules:
    return user

@router.put("/password", dependencies=[Depends(validate_is_authenticated)], description='Required authentication')
async def change_password_api(user: Annotated[User, Depends(get_current_user)], db_session: DBSessionDep, data: ChangePasswordSchema) -> UserResponseRules:
    return await change_password(db_session, data, user)